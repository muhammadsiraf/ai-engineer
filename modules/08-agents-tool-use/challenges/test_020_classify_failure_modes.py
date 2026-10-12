import pytest


def _load():
    import importlib.util

    path = __file__.replace(
        "test_020_classify_failure_modes.py", "020_classify_failure_modes.py"
    )
    spec = importlib.util.spec_from_file_location("chal_m8_020", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


def call(name, args):
    return {"type": "tool_call", "name": name, "args": args}


OK = {"type": "tool_result", "ok": True, "result": "fine"}


def err(kind):
    return {"type": "tool_result", "ok": False, "error_kind": kind, "error": "boom"}


def ans(text="done"):
    return {"type": "answer", "text": text}


class TestCallSignature:
    def test_argument_order_does_not_matter(self, chal):
        assert chal.call_signature("f", {"a": 1, "b": 2}) == chal.call_signature(
            "f", {"b": 2, "a": 1}
        )

    def test_differs_by_name_or_args(self, chal):
        assert chal.call_signature("f", {"a": 1}) != chal.call_signature("g", {"a": 1})
        assert chal.call_signature("f", {"a": 1}) != chal.call_signature("f", {"a": 2})


class TestErrorKinds:
    def test_histogram(self, chal):
        traj = [err("runtime"), OK, err("runtime"), err("invalid_args")]
        assert chal.error_kinds(traj) == {"runtime": 2, "invalid_args": 1}

    def test_no_errors(self, chal):
        assert chal.error_kinds([ans("hi")]) == {}


class TestClassify:
    def test_success(self, chal):
        traj = [call("search", {"q": "x"}), OK, ans()]
        assert chal.classify(traj) == "success"

    def test_no_tools(self, chal):
        assert chal.classify([ans("Paris")]) == "no_tools"

    def test_misuse_recovered_still_counts(self, chal):
        traj = [
            call("get_order", {"id": 5}),
            err("invalid_args"),
            call("get_order", {"id": "A-5"}),
            OK,
            ans(),
        ]
        assert chal.classify(traj) == "misuse"

    def test_unknown_tool_is_misuse(self, chal):
        assert chal.classify([call("nope", {}), err("unknown_tool"), ans()]) == "misuse"

    def test_thrash_precedence_over_misuse(self, chal):
        traj = [
            call("s", {"q": 1}),
            err("invalid_args"),
            call("s", {"q": 1}),
            err("invalid_args"),
            call("s", {"q": 1}),
        ]
        assert chal.classify(traj) == "thrash"

    def test_thrash_with_reordered_args(self, chal):
        traj = [
            call("s", {"q": 1, "lang": "en"}),
            err("runtime"),
            call("s", {"lang": "en", "q": 1}),
            err("runtime"),
            call("s", {"q": 1, "lang": "en"}),
        ]
        assert chal.classify(traj) == "thrash"

    def test_two_repeats_are_not_thrash(self, chal):
        traj = [call("s", {}), OK, call("s", {}), OK, ans()]
        assert chal.classify(traj) == "success"

    def test_premature(self, chal):
        traj = [call("refund", {"id": "x"}), err("runtime"), ans("refund processed")]
        assert chal.classify(traj) == "premature"

    def test_unfinished(self, chal):
        assert chal.classify([call("search", {"q": "x"}), OK]) == "unfinished"

    def test_empty_rejected(self, chal):
        with pytest.raises(ValueError):
            chal.classify([])


class TestShapeRates:
    def test_four_shapes(self, chal):
        runs = [
            [call("search", {"q": "x"}), OK, ans()],  # success
            [ans("Paris")],  # no_tools
            [call("nope", {}), err("unknown_tool"), ans()],  # misuse
            [call("refund", {"id": "x"}), err("runtime"), ans()],  # premature
        ]
        rates = chal.shape_rates(runs)
        assert rates == {
            "success": 0.25,
            "no_tools": 0.25,
            "misuse": 0.25,
            "premature": 0.25,
        }

    def test_single_run(self, chal):
        assert chal.shape_rates([[ans("hi)")]]) == {"no_tools": 1.0}
