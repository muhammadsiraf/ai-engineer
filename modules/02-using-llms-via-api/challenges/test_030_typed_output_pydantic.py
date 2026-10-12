import json

import pytest


pydantic = pytest.importorskip("pydantic")


def _load():
    import importlib.util

    path = __file__.replace("test_030_typed_output_pydantic.py", "030_typed_output_pydantic.py")
    spec = importlib.util.spec_from_file_location("chal_m2_030", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


VALID = {
    "category": "billing",
    "priority": "high",
    "confidence": 0.9,
    "rationale": "duplicate charge reported",
}


class TestStripFences:
    def test_bare_json(self, chal):
        raw = json.dumps(VALID)
        assert chal.strip_fences(raw) == raw

    def test_fenced(self, chal):
        raw = "```json\n" + json.dumps(VALID) + "\n```"
        assert json.loads(chal.strip_fences(raw)) == VALID

    def test_prose_wrapper(self, chal):
        raw = 'Sure! Here is the JSON:\n{"a": 1}\nHope that helps!'
        assert chal.strip_fences(raw) == '{"a": 1}'

    def test_nested_braces(self, chal):
        raw = 'prefix {"a": {"b": 2}} suffix'
        assert chal.strip_fences(raw) == '{"a": {"b": 2}}'


class TestParseTriage:
    def test_valid(self, chal):
        t = chal.parse_triage(json.dumps(VALID))
        assert t.category == "billing"
        assert t.confidence == pytest.approx(0.9)

    def test_fenced_valid(self, chal):
        t = chal.parse_triage("```json\n" + json.dumps(VALID) + "\n```")
        assert t.priority == "high"

    def test_bad_category_raises(self, chal):
        bad = {**VALID, "category": "mystery"}
        with pytest.raises(pydantic.ValidationError):
            chal.parse_triage(json.dumps(bad))

    def test_confidence_out_of_range_raises(self, chal):
        bad = {**VALID, "confidence": 1.5}
        with pytest.raises(pydantic.ValidationError):
            chal.parse_triage(json.dumps(bad))

    def test_too_long_rationale_raises(self, chal):
        bad = {**VALID, "rationale": "x" * 201}
        with pytest.raises(pydantic.ValidationError):
            chal.parse_triage(json.dumps(bad))

    def test_unparseable_raises_json_error(self, chal):
        with pytest.raises(json.JSONDecodeError):
            chal.parse_triage("this is not json at all")


class TestRetry:
    def test_first_try_success_no_feedback(self, chal):
        calls = []

        def call_fn(feedback):
            calls.append(feedback)
            return json.dumps(VALID)

        chal.parse_with_retry(call_fn)
        assert calls == [None]

    def test_retry_with_error_feedback(self, chal):
        calls = []

        def call_fn(feedback):
            calls.append(feedback)
            if feedback is None:
                return json.dumps({**VALID, "category": "bogus"})
            return json.dumps(VALID)

        out = chal.parse_with_retry(call_fn)
        assert out.category == "billing"
        assert calls[0] is None
        assert calls[1] is not None and "category" in calls[1]

    def test_exhaustion_raises(self, chal):
        def call_fn(feedback):
            return json.dumps({**VALID, "priority": "urgent"})

        with pytest.raises(pydantic.ValidationError):
            chal.parse_with_retry(call_fn, max_attempts=2)

    def test_three_attempts_allowed(self, chal):
        state = {"n": 0}

        def call_fn(feedback):
            state["n"] += 1
            if state["n"] < 3:
                return json.dumps({**VALID, "confidence": 42})
            return json.dumps(VALID)

        out = chal.parse_with_retry(call_fn, max_attempts=3)
        assert out.category == "billing"
        assert state["n"] == 3

    def test_json_error_triggers_retry(self, chal):
        calls = []

        def call_fn(feedback):
            calls.append(feedback)
            return "not json" if feedback is None else json.dumps(VALID)

        assert chal.parse_with_retry(call_fn).category == "billing"
        assert len(calls) == 2
