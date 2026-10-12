import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_020_chain_of_thought.py", "020_chain_of_thought.py")
    spec = importlib.util.spec_from_file_location("chal_m2_020", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


FACTS = {"coffee": 4, "muffin": 3, "tip": 2, "tax": 1}


class TestTwoHop:
    def test_simple_sum(self, chal):
        client = chal.MockReasoner(FACTS)
        assert chal.solve_two_hop(client, FACTS, "coffee", "muffin") == 7

    def test_history_grows(self, chal):
        client = chal.MockReasoner(FACTS)
        chal.solve_two_hop(client, FACTS, "coffee", "tip")
        # FACT a, FACT b, ADD -> at least 3 user turns
        user_turns = [p for p in client.prompts_seen]
        assert len(user_turns) >= 3
        assert user_turns[0].startswith("FACT")
        assert user_turns[1].startswith("FACT")
        assert user_turns[2].startswith("ADD")

    def test_missing_fact_raises(self, chal):
        client = chal.MockReasoner(FACTS)
        with pytest.raises(ValueError):
            chal.solve_two_hop(client, FACTS, "coffee", "unicorn")

    def test_values_from_responses_not_lookup(self, chal):
        # sabotage the dict AFTER construction; orchestrator must use responses
        client = chal.MockReasoner(dict(FACTS))
        client.facts["coffee"] = 999
        assert chal.solve_two_hop(client, client.facts, "coffee", "muffin") == 7


class TestBudget:
    def test_chained_adds(self, chal):
        client = chal.MockReasoner(FACTS)
        steps = [
            ("FACT", "coffee"),   # 4      -> #0
            ("FACT", "muffin"),   # 3      -> #1
            ("ADD", "#0", "#1"),  # 7      -> #2
            ("ADD", "#2", "#1"),  # 10     -> #3
        ]
        assert chal.solve_with_budget(client, FACTS, steps) == 10

    def test_literal_operands(self, chal):
        client = chal.MockReasoner(FACTS)
        steps = [("ADD", "2", "3")]
        assert chal.solve_with_budget(client, FACTS, steps) == 5

    def test_missing_fact_raises(self, chal):
        client = chal.MockReasoner(FACTS)
        with pytest.raises(ValueError):
            chal.solve_with_budget(client, FACTS, [("FACT", "nope")])

    def test_bad_step_raises(self, chal):
        client = chal.MockReasoner(FACTS)
        with pytest.raises(ValueError):
            chal.solve_with_budget(client, FACTS, [("SUBTRACT", "1", "2")])


class TestParseFinal:
    def test_basic(self, chal):
        assert chal.parse_final("Let me add. Answer: 42") == 42

    def test_case_insensitive(self, chal):
        assert chal.parse_final("answer: 7") == 7

    def test_negative(self, chal):
        assert chal.parse_final("Answer: -3") == -3

    def test_missing_raises(self, chal):
        with pytest.raises(ValueError):
            chal.parse_final("I could not compute.")
        with pytest.raises(ValueError):
            chal.parse_final("The answer is not present")
