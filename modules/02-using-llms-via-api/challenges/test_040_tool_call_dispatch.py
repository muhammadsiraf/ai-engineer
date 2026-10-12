import json

import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_040_tool_call_dispatch.py", "040_tool_call_dispatch.py")
    spec = importlib.util.spec_from_file_location("chal_m2_040", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


SCHEMA = {
    "type": "object",
    "properties": {"order_id": {"type": "string"}},
    "required": ["order_id"],
}


@pytest.fixture()
def registry(chal):
    reg = chal.ToolRegistry()

    def get_order(order_id: str):
        return {"order_id": order_id, "status": "shipped"}

    reg.register("get_order", get_order, SCHEMA)
    return reg


class TestRegistry:
    def test_register_and_get(self, registry):
        assert registry.get("get_order") is not None
        assert registry.get("nope") is None

    def test_duplicate_raises(self, registry):
        with pytest.raises(ValueError):
            registry.register("get_order", lambda: 1, SCHEMA)

    def test_specs_shape(self, registry):
        specs = registry.specs()
        assert specs == [
            {"type": "function", "function": {"name": "get_order", "parameters": SCHEMA}}
        ]


class TestSafeExecute:
    def test_success(self, registry):
        out = registry.safe_execute(
            "get_order", json.dumps({"order_id": "A-1"}), call_id="c1"
        )
        assert out["tool_call_id"] == "c1"
        assert out["result"] == {"order_id": "A-1", "status": "shipped"}
        assert "error" not in out

    def test_unknown_tool_is_error_not_raise(self, registry):
        out = registry.safe_execute("delete_db", "{}", call_id="c2")
        assert out["tool_call_id"] == "c2"
        assert "error" in out

    def test_bad_json_is_error(self, registry):
        out = registry.safe_execute("get_order", "{not json", call_id="c3")
        assert "error" in out

    def test_missing_required_is_error_and_fn_not_called(self, registry):
        calls = []

        def spy(order_id: str):
            calls.append(order_id)
            return {}

        reg = registry
        reg.register("spy", spy, SCHEMA)
        out = reg.safe_execute("spy", json.dumps({}), call_id="c4")
        assert "error" in out
        assert calls == []

    def test_wrong_type_is_error(self, registry):
        out = registry.safe_execute("get_order", json.dumps({"order_id": 7}), call_id="c5")
        assert "error" in out

    def test_unexpected_key_is_error(self, registry):
        out = registry.safe_execute(
            "get_order", json.dumps({"order_id": "A", "extra": 1}), call_id="c6"
        )
        assert "error" in out

    def test_fn_exception_becomes_error_entry(self, chal, registry):
        def boom(order_id: str):
            raise RuntimeError("downstream 500")

        registry.register("boom", boom, SCHEMA)
        out = registry.safe_execute("boom", json.dumps({"order_id": "x"}), call_id="c7")
        assert "downstream 500" in out["error"]
        assert out["tool_call_id"] == "c7"


class TestRunLoop:
    def test_immediate_text(self, chal, registry):
        client = chal.MockToolModel(["All done."])
        assert chal.run_loop(client, registry, [{"role": "user", "content": "hi"}]) == "All done."

    def test_one_round_then_answer(self, chal, registry):
        client = chal.MockToolModel(
            [
                chal.ToolCall("t1", "get_order", json.dumps({"order_id": "A-9"})),
                "Your order A-9 has shipped.",
            ]
        )
        msgs = [{"role": "user", "content": "where is A-9?"}]
        final = chal.run_loop(client, registry, msgs)
        assert final == "Your order A-9 has shipped."
        # the second request must contain the assistant tool_call msg + tool result
        second = client.history[1]
        assert any(m.get("role") == "assistant" for m in second)
        tool_msgs = [m for m in second if m.get("role") == "tool"]
        assert len(tool_msgs) == 1
        assert tool_msgs[0]["tool_call_id"] == "t1"
        assert json.loads(tool_msgs[0]["content"])["status"] == "shipped"

    def test_error_result_feeds_back_not_raises(self, chal, registry):
        client = chal.MockToolModel(
            [
                chal.ToolCall("t2", "unknown_tool", "{}"),
                "I could not do that.",
            ]
        )
        final = chal.run_loop(client, registry, [{"role": "user", "content": "x"}])
        assert final == "I could not do that."

    def test_loop_budget(self, chal, registry):
        client = chal.MockToolModel(
            [chal.ToolCall(f"t{i}", "get_order", json.dumps({"order_id": "A"})) for i in range(10)]
        )
        with pytest.raises(RuntimeError):
            chal.run_loop(client, registry, [{"role": "user", "content": "x"}], max_rounds=3)
