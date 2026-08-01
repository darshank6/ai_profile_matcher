import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar


logger = logging.getLogger(__name__)

T = TypeVar("T")


async def run_blocking_io(
    func: Callable[..., T],
    *args: Any,
    **kwargs: Any,
) -> T:
    """
    Run blocking synchronous code in a worker thread.

    Use this when the project still uses synchronous SQLAlchemy Session,
    requests, file parsing, or CPU-light blocking logic inside async services.
    """

    return await asyncio.to_thread(
        func,
        *args,
        **kwargs,
    )


async def gather_with_concurrency(
    limit: int,
    tasks: list[Awaitable[T]],
) -> list[T]:
    """
    Run awaitable tasks with concurrency limit.

    This prevents overloading external APIs such as embedding endpoints
    or LLM services.
    """

    semaphore = asyncio.Semaphore(limit)

    async def sem_task(task: Awaitable[T]) -> T:
        async with semaphore:
            return await task

    return await asyncio.gather(
        *[
            sem_task(task)
            for task in tasks
        ]
    )


async def with_timeout(
    awaitable: Awaitable[T],
    timeout_seconds: float,
) -> T:
    """
    Apply timeout to an async task.
    """

    return await asyncio.wait_for(
        awaitable,
        timeout=timeout_seconds,
    )


async def retry_async(
    func: Callable[..., Awaitable[T]],
    retries: int = 3,
    delay_seconds: float = 1.0,
    *args: Any,
    **kwargs: Any,
) -> T:
    """
    Retry an async function.

    Useful for transient network failures during embedding or LLM calls.
    """

    last_exception: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            return await func(
                *args,
                **kwargs,
            )
        except Exception as exc:
            last_exception = exc
            logger.warning(
                "Async retry failed | attempt=%s retries=%s error=%s",
                attempt,
                retries,
                str(exc),
            )

            if attempt < retries:
                await asyncio.sleep(delay_seconds)

    if last_exception is not None:
        raise last_exception

    raise RuntimeError("retry_async failed without exception details")