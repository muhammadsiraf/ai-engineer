import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_080_retry_with_backoff.py", "080_retry_with_backoff.py")
    spec = importlib.util.spec_from_file_location("chal_m2_080", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


def flaky(fails, exc=None):
    """fn that fails N times then succeeds."""
    state = {"n": 0}

    def fn():
        state["n"] += 1
        if state["n"] <= fails:
            raise exc if exc is not None else Exception("boom")
        return f"ok-after-{state['n']}"

    fn.state = state
    return fn


@pytest.fixture()
def sleeps():
    return []


@pytest.fixture()
def no_jitter():
    return lambda d: 0.0


class TestClassify:
    def test_retryable_kinds(self, chal):
        assert chal.is_retryable(chal.RateLimitError())
        assert chal.is_retryable(chal.ServerError())

    def test_not_retryable(self, chal):
        assert not chal.is_retryable(chal.BadRequest())
        assert not chal.is_retryable(ValueError())


class TestHappyPath:
    def test_success_first_try_no_sleep(self, chal, sleeps, no_jitter):
        assert chal.call_with_retry(lambda: 42, sleep=sleeps.append, jitter=no_jitter) == 42
        assert sleeps == []


class TestRetries:
    def test_recovers_after_failures(self, chal, sleeps, no_jitter):
        fn = flaky(2)
        assert chal.call_with_retry(fn, base=1.0, sleep=sleeps.append, jitter=no_jitter) == "ok-after-3"

    def test_backoff_sequence(self, chal, sleeps, no_jitter):
        fn = flaky(3)
        chal.call_with_retry(fn, base=1.0, cap=100, sleep=sleeps.append, jitter=no_jitter)
        assert sleeps == [1.0, 2.0, 4.0]

    def test_cap_applied(self, chal, sleeps, no_jitter):
        fn = flaky(4)
        chal.call_with_retry(fn, base=2.0, cap=3.0, sleep=sleeps.append, jitter=no_jitter)
        assert sleeps == [2.0, 3.0, 3.0, 3.0]

    def test_jitter_added_before_cap(self, chal, sleeps):
        fn = flaky(2)
        chal.call_with_retry(
            fn, base=1.0, cap=2.5, sleep=sleeps.append, jitter=lambda d: 0.5
        )
        # delays: 1.5, then min(2.0+0.5, 2.5)=2.5
        assert sleeps == [1.5, 2.5]

    def test_exhaustion_reraises(self, chal, sleeps, no_jitter):
        def always():
            raise chal.ServerError("dead")

        with pytest.raises(chal.ServerError, match="dead"):
            chal.call_with_retry(always, max_retries=2, sleep=sleeps.append, jitter=no_jitter)
        assert len(sleeps) == 2  # max_retries attempts that sleep

    def test_attempt_count(self, chal, sleeps, no_jitter):
        fn = flaky(10)
        with pytest.raises(Exception):
            chal.call_with_retry(fn, max_retries=3, sleep=sleeps.append, jitter=no_jitter)
        assert fn.state["n"] == 4  # 1 initial + 3 retries


class TestRetryAfter:
    def test_honors_retry_after_when_larger(self, chal, sleeps, no_jitter):
        state = {"n": 0}

        def fn():
            state["n"] += 1
            if state["n"] == 1:
                raise chal.RateLimitError("calm down", retry_after=30.0)
            return "ok"

        chal.call_with_retry(fn, base=1.0, sleep=sleeps.append, jitter=no_jitter)
        assert sleeps == [30.0]

    def test_backoff_wins_when_larger(self, chal, sleeps, no_jitter):
        state = {"n": 0}

        def fn():
            state["n"] += 1
            if state["n"] == 1:
                raise chal.RateLimitError("tiny", retry_after=0.1)
            return "ok"

        chal.call_with_retry(fn, base=5.0, sleep=sleeps.append, jitter=no_jitter)
        assert sleeps == [5.0]


class TestBadRequest:
    def test_no_retry_no_sleep(self, chal, sleeps, no_jitter):
        calls = {"n": 0}

        def fn():
            calls["n"] += 1
            raise chal.BadRequest("your fault")

        with pytest.raises(chal.BadRequest):
            chal.call_with_retry(fn, sleep=sleeps.append, jitter=no_jitter)
        assert calls["n"] == 1
        assert sleeps == []
