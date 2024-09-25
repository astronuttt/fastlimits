from typing import (
    Awaitable,
    Callable,
)

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .dependencies import BaseLimiterDependency
from .limiter import FastAPIRateLimiter


class RateLimitingMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        limiter: FastAPIRateLimiter | None = None,
    ) -> None:
        if not limiter:
            limiter = FastAPIRateLimiter()
        self.limiter = limiter
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request.state.limiter = self.limiter
        response = await call_next(request)
        try:
            limit: BaseLimiterDependency = request.state.limit
            limit_keys: list[str] = request.state.limit_keys
        except AttributeError:
            return response
        if (
            limit.no_hit_status_codes
            and response.status_code in limit.no_hit_status_codes
        ):
            return response

        await self.limiter.strategy.hit(
            limit.item,
            *limit_keys,
        )
        return response
