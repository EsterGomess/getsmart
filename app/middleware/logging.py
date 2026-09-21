"""Logging middleware."""
import time
import structlog
from asgi_correlation_id import correlation_id
from structlog.contextvars import bind_contextvars, clear_contextvars
from fastapi import Request

logger = structlog.get_logger()


async def log_requests(request: Request, call_next):
    """Log incoming requests and their response times."""
    clear_contextvars()
    bind_contextvars(correlation_id=correlation_id.get())

    start_time = time.perf_counter()
    response = await call_next(request)
    response_time = time.perf_counter() - start_time

    logger.info(
        "request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        response_time=f"{response_time:.3f}s",
    )
    return response
