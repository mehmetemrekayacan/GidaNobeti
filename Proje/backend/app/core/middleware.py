"""
Custom Middleware - Request Logging (TASK-BE-019)
"""
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from loguru import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Her request'i loglar: method, path, status, duration, client_ip."""

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path

        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        if response.status_code >= 500:
            logger.error(
                "{} {} -> {} ({}ms) ip={}",
                method, path, response.status_code, round(duration_ms, 2), client_ip,
            )
        elif response.status_code >= 400:
            logger.warning(
                "{} {} -> {} ({}ms) ip={}",
                method, path, response.status_code, round(duration_ms, 2), client_ip,
            )
        else:
            logger.info(
                "{} {} -> {} ({}ms) ip={}",
                method, path, response.status_code, round(duration_ms, 2), client_ip,
            )

        return response
