import pytest

from app.utils.decorators import async_retry, retry


class CustomError(Exception):
    pass


class NonRetryError(Exception):
    pass


def test_retry_success():
    @retry()
    def func():
        return 42

    assert func() == 42


def test_retry_retries_then_success(monkeypatch):
    calls = {"count": 0}

    @retry(max_retries=3)
    def func():
        calls["count"] += 1
        if calls["count"] < 2:
            raise CustomError()
        return "ok"

    assert func() == "ok"
    assert calls["count"] == 2


def test_retry_max_retries_raises():
    @retry(max_retries=2)
    def func():
        raise CustomError()

    with pytest.raises(CustomError):
        func()


def test_retry_sleep(monkeypatch):
    called = {"sleep": 0}

    def fake_sleep(t):
        called["sleep"] += 1

    monkeypatch.setattr("app.utils.decorators.sleep", fake_sleep)
    calls = {"count": 0}

    @retry(max_retries=3, sleep_time=0.1)
    def func():
        calls["count"] += 1
        raise CustomError()

    with pytest.raises(CustomError):
        func()
    assert called["sleep"] == 2


def test_retry_raises_on_exception_false():
    @retry(max_retries=2, raises_on_exception=False)
    def func():
        raise CustomError()

    assert func() is None


def test_retry_non_retry_exceptions():
    @retry(max_retries=3, non_retry_exceptions=(NonRetryError,))
    def func():
        raise NonRetryError()

    with pytest.raises(NonRetryError):
        func()


@pytest.mark.asyncio
async def test_async_retry_success():
    @async_retry()
    async def func():
        return 99

    assert await func() == 99


@pytest.mark.asyncio
async def test_async_retry_retries_then_success():
    calls = {"count": 0}

    @async_retry(max_retries=3)
    async def func():
        calls["count"] += 1
        if calls["count"] < 2:
            raise CustomError()
        return "ok"

    assert await func() == "ok"
    assert calls["count"] == 2


@pytest.mark.asyncio
async def test_async_retry_max_retries_raises():
    @async_retry(max_retries=2)
    async def func():
        raise CustomError()

    with pytest.raises(CustomError):
        await func()


@pytest.mark.asyncio
async def test_async_retry_sleep(monkeypatch):
    called = {"sleep": 0}

    async def fake_asyncio_sleep(t):
        called["sleep"] += 1

    monkeypatch.setattr("asyncio.sleep", fake_asyncio_sleep)
    calls = {"count": 0}

    @async_retry(max_retries=3, sleep_time=0.1)
    async def func():
        calls["count"] += 1
        raise CustomError()

    with pytest.raises(CustomError):
        await func()
    assert called["sleep"] == 2


@pytest.mark.asyncio
async def test_async_retry_raises_on_exception_false():
    @async_retry(max_retries=2, raises_on_exception=False)
    async def func():
        raise CustomError()

    assert await func() is None


@pytest.mark.asyncio
async def test_async_retry_non_retry_exceptions():
    @async_retry(max_retries=3, non_retry_exceptions=(NonRetryError,))
    async def func():
        raise NonRetryError()

    with pytest.raises(NonRetryError):
        await func()


@pytest.mark.asyncio
async def test_retry_guard_raises_when_event_loop_running(monkeypatch):
    called = {"sleep": 0}

    def fake_sleep(_: float) -> None:
        called["sleep"] += 1

    monkeypatch.setattr("app.utils.decorators.sleep", fake_sleep)

    @retry(max_retries=3, sleep_time=0.1)
    def func():
        raise CustomError()

    with pytest.raises(RuntimeError, match="Use async_retry\\(\\) instead"):
        func()

    assert called["sleep"] == 0
