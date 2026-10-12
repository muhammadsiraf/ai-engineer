import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_010_dispatch_tool_call.py", "010_dispatch_tool_call.py")
    spec = importlib.util.spec_from_file_location("chal_m8_010", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


SPEC = {
    "name": "get_order_status",
    "description": "Look up an order by ID.",
    "parameters": {
        "type": "object",
        "properties": {
            "order_id": {"type": "string"},
            "units": {"type": "string", "enum": ["c", "f"]},
        },
        "required": ["order_id"],
    },
}


def get_order_status(order_id, units=None):
    return f"order {order_id}: shipped"


REGISTRY = {"get_order_status": (SPEC, get_order_status)}


def call(name="get_order_status", **kwargs):
    return {"name": name, "arguments": kwargs}


class TestValidateArgs:
    def test_valid_args_pass(self, chal):
        assert chal.validate_args(SPEC, {"order_id": "A-1", "units": "c"}) is None

    def test_missing_required(self, chal):
        with pytest.raises(ValueError) as e:
            chal.validate_args(SPEC, {})
        assert "order_id" in str(e.value)

    def test_unknown_argument(self, chal):
        with pytest.raises(ValueError) as e:
            chal.validate_args(SPEC, {"order_id": "A-1", "city": "Oslo"})
        assert "city" in str(e.value)

    def test_wrong_type(self, chal):
        with pytest.raises(ValueError) as e:
            chal.validate_args(SPEC, {"order_id": 1024})
        assert "order_id" in str(e.value)

    def test_enum_violation(self, chal):
        with pytest.raises(ValueError) as e:
            chal.validate_args(SPEC, {"order_id": "A-1", "units": "k"})
        assert "units" in str(e.value)

    def test_bool_is_not_integer(self, chal):
        spec = {"parameters": {"properties": {"n": {"type": "integer"}}, "required": []}}
        with pytest.raises(ValueError):
            chal.validate_args(spec, {"n": True})
        assert chal.validate_args(spec, {"n": 3}) is None

    def test_integer_accepted_for_number(self, chal):
        spec = {"parameters": {"properties": {"x": {"type": "number"}}, "required": []}}
        assert chal.validate_args(spec, {"x": 2}) is None


class TestDispatch:
    def test_happy_path(self, chal):
        out = chal.dispatch(REGISTRY, call(order_id="A-1024"))
        assert out == {"ok": True, "result": "order A-1024: shipped"}

    def test_unknown_tool(self, chal):
        out = chal.dispatch(REGISTRY, call(name="delete_calendar", x=1))
        assert out["ok"] is False
        assert "unknown tool" in out["error"]

    def test_validation_error_becomes_error_dict(self, chal):
        out = chal.dispatch(REGISTRY, call())  # missing order_id
        assert out["ok"] is False
        assert "order_id" in out["error"]

    def test_function_not_called_on_invalid(self, chal):
        seen = []

        def spy(order_id):
            seen.append(order_id)
            return "x"

        reg = {"get_order_status": (SPEC, spy)}
        out = chal.dispatch(reg, call())  # missing order_id
        assert out["ok"] is False
        assert seen == []

    def test_valid_enum_forwarded(self, chal):
        out = chal.dispatch(REGISTRY, call(order_id="A-1", units="f"))
        assert out["ok"] is True


class TestDispatchAll:
    def test_all_executed_in_order(self, chal):
        calls = [call(order_id="A-1"), call(order_id="A-2")]
        outs = chal.dispatch_all(REGISTRY, calls)
        assert [o["result"] for o in outs] == [
            "order A-1: shipped",
            "order A-2: shipped",
        ]

    def test_failure_does_not_stop_the_rest(self, chal):
        calls = [call(order_id="A-1"), call(name="nope"), call(order_id="A-3")]
        outs = chal.dispatch_all(REGISTRY, calls)
        assert outs[0]["ok"] is True
        assert outs[1]["ok"] is False
        assert outs[2]["ok"] is True

    def test_empty(self, chal):
        assert chal.dispatch_all(REGISTRY, []) == []
