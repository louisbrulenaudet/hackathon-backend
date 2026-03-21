import asyncio
import random
from collections.abc import Awaitable, Callable
from time import sleep
from typing import ParamSpec, TypeVar

__all__ = [
    "retry",
    "async_retry",
]


P = ParamSpec("P")
R = TypeVar("R")


def _compute_retry_delay(sleep_time: int | float, attempt: int) -> float:
    """
    Compute an attempt-based backoff delay with jitter.

    Full-jitter (uniform in [0, base_delay]) reduces thundering herd impact when many requests retry concurrently after the same downstream failure.
    """  # pragma: no cover
    base_delay = float(sleep_time) * (2**attempt)
    return random.uniform(0, base_delay)


def _is_event_loop_running() -> bool:
    """
    Return True when called from within an active asyncio event loop.

    This is used to prevent the sync retry decorator from performing blocking   sleeps inside async contexts.
    """  # pragma: no cover
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return False
    return True


def _should_raise(
    exc: Exception,
    attempt: int,
    max_retries: int,
    raises_on_exception: bool,
    non_retry_exceptions: tuple[type[Exception], ...],
) -> bool:
    """
    Return True when the caught exception should be re-raised.
    """  # pragma: no cover
    if not raises_on_exception:
        return False
    return attempt == max_retries - 1 or (
        bool(non_retry_exceptions) and isinstance(exc, non_retry_exceptions)
    )


def retry(
    max_retries: int = 3,
    sleep_time: int | float = 0,
    raises_on_exception: bool = True,
    non_retry_exceptions: tuple[type[Exception], ...] = (),
) -> Callable[[Callable[P, R]], Callable[P, R | None]]:
    """
    Decorator to retry a function call on exception.

    Args:
        max_retries (int): Maximum number of retries before giving up.
        sleep_time (int | float): Time to sleep between retries.
        raises_on_exception (bool): If True, re-raises the exception after max retries.
        non_retry_exceptions (tuple[type[Exception], ...]): Exceptions that should not trigger a retry.

    Returns:
        Callable[[Callable[..., Any]], Callable[..., Any]]: Decorated function that retries on exception.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R | None]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
            if _is_event_loop_running():
                raise RuntimeError(
                    "retry() must not be used inside an async context. "
                    "Use async_retry() instead."
                )
            for i in range(max_retries):
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    if _should_raise(
                        e, i, max_retries, raises_on_exception, non_retry_exceptions
                    ):
                        raise e
                    if sleep_time:
                        sleep(_compute_retry_delay(sleep_time, i))

        return wrapper

    return decorator


def async_retry(
    max_retries: int = 3,
    sleep_time: int | float = 0,
    raises_on_exception: bool = True,
    non_retry_exceptions: tuple[type[Exception], ...] = (),
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R | None]]]:
    """
    Async decorator to retry a coroutine function call on exception.

    Args:
        max_retries (int): Maximum number of retries before giving up.
        sleep_time (int | float): Time to sleep between retries.
        raises_on_exception (bool): If True, re-raises the exception after max retries.
        non_retry_exceptions (tuple[type[Exception], ...]): Exceptions that should not trigger a retry.

    Returns:
        Callable[[Callable[..., Any]], Callable[..., Any]]: Decorated async function that retries on exception.
    """

    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R | None]]:
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
            for i in range(max_retries):
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    if _should_raise(
                        e, i, max_retries, raises_on_exception, non_retry_exceptions
                    ):
                        raise e
                    if sleep_time:
                        await asyncio.sleep(_compute_retry_delay(sleep_time, i))

        return wrapper

    return decorator
