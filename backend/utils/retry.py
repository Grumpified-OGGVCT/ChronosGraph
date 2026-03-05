"""Retry decorator with exponential backoff for API calls."""

import asyncio
import functools
import logging
from typing import Any, Callable

logger = logging.getLogger("chronosgraph.retry")


class ProcessingError(Exception):
    pass


def with_retry(max_retries: int = 3, base_delay: float = 2.0,
               retryable_status_codes: tuple[int, ...] = (429, 500, 502, 503, 504)) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exc = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    code = getattr(e, "status_code", None) or getattr(e, "code", None)
                    retryable = code in retryable_status_codes if code else True
                    if attempt < max_retries and retryable:
                        delay = base_delay * (2 ** attempt)
                        logger.warning("Attempt %d/%d for %s failed. Retrying in %.1fs...",
                                       attempt + 1, max_retries + 1, func.__name__, delay)
                        await asyncio.sleep(delay)
                    else:
                        break
            raise ProcessingError(f"{func.__name__} failed after {max_retries + 1} attempts: {last_exc}") from last_exc
        return wrapper
    return decorator
