import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_040_prefix_cache_hits_under_routing.py", "040_prefix_cache_hits_under_routing.py")
    spec = importlib.util.spec_from_file_location("chal_m6_040", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


KEYS3 = ["sys_a", "sys_b", "sys_c"]


def cycle_3_keys(n_reps: int) -> list:
    return [(KEYS3[i % 3], 100) for i in range(30)]


class TestShardFor:
    def test_single_replica_is_zero(self, chal):
        assert chal.shard_for("anything", 1) == 0

    def test_deterministic(self, chal):
        assert all(
            chal.shard_for(f"key{i}", 8) == chal.shard_for(f"key{i}", 8)
            for i in range(50)
        )

    def test_in_range(self, chal):
        assert all(0 <= chal.shard_for(f"k{i}", 4) < 4 for i in range(200))

    def test_bad_n_raises(self, chal):
        with pytest.raises(ValueError):
            chal.shard_for("k", 0)


class TestHandComputed:
    def test_unlimited_single_replica(self, chal):
        # 30 requests, 3 distinct prefixes → 3 misses
        assert chal.simulate(cycle_3_keys(1), 1, "affinity") == pytest.approx(0.9)

    def test_lru_thrash_on_strict_cycle(self, chal):
        # capacity 2 < 3 keys cycling → every request evicts its own key
        assert chal.simulate(cycle_3_keys(1), 1, "affinity", cache_capacity=2) == pytest.approx(0.0)

    def test_lru_pattern_hits(self, chal):
        # k0,k0,k1,k1,k2,k2 × 5 with capacity 2 → 3 hits per 6 requests
        reqs = [(k, 100) for _ in range(5) for k in ("k0", "k0", "k1", "k1", "k2", "k2")]
        assert chal.simulate(reqs, 1, "affinity", cache_capacity=2) == pytest.approx(0.5)

    def test_token_weighting(self, chal):
        # same 3 misses, but big tokens on the hit requests
        reqs = [("k0", 900), ("k1", 10_000), ("k2", 10_000), ("k1", 10_000)]
        # misses: k0(900), k1(10k), k2(10k); hit: last k1 (10k)
        assert chal.simulate(reqs, 1, "affinity") == pytest.approx(10_000 / 30_900)

    def test_empty_log(self, chal):
        assert chal.simulate([], 4, "affinity") == 0.0


class TestPolicies:
    FIVE_KEYS = ["p0", "p1", "p2", "p3", "p4"]

    def REQUESTS(self):
        return [(self.FIVE_KEYS[i % 5], 100) for i in range(1000)]

    def test_round_robin_thrash_capacity_one(self, chal):
        # each replica receives all 5 keys in rotation → 0% after warmup
        assert chal.simulate(self.REQUESTS(), 4, "round_robin", cache_capacity=1) == 0.0

    def test_affinity_beats_round_robin(self, chal):
        rr = chal.simulate(self.REQUESTS(), 4, "round_robin", cache_capacity=1)
        aff = chal.simulate(self.REQUESTS(), 4, "affinity", cache_capacity=1)
        assert aff > rr

    def test_affinity_deterministic(self, chal):
        a = chal.simulate(self.REQUESTS(), 4, "affinity", cache_capacity=1)
        b = chal.simulate(self.REQUESTS(), 4, "affinity", cache_capacity=1)
        assert a == b

    def test_unlimited_cache_both_good_but_affinity_not_worse(self, chal):
        rr = chal.simulate(self.REQUESTS(), 4, "round_robin")
        aff = chal.simulate(self.REQUESTS(), 4, "affinity")
        assert aff >= rr
        assert rr > 0.9  # warmup cost only


class TestValidation:
    def test_bad_policy(self, chal):
        with pytest.raises(ValueError):
            chal.simulate([("k", 1)], 2, "random")

    def test_bad_replicas(self, chal):
        with pytest.raises(ValueError):
            chal.simulate([("k", 1)], 0, "affinity")

    def test_bad_capacity(self, chal):
        with pytest.raises(ValueError):
            chal.simulate([("k", 1)], 2, "affinity", cache_capacity=0)
