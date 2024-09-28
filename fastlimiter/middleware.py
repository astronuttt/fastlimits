from typing import TYPE_CHECKING, Awaitable, Callable

from fastapi import Request, Response
from limits.aio.strategies import RateLimiter
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .functions import get_remote_address
from .types import CallableMiddlewareKey
from .utils import ensure_list

if TYPE_CHECKING:
    from .dependencies import BaseLimiterDependency


class RateLimitingMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        strategy: RateLimiter,
        keys: CallableMiddlewareKey | list[CallableMiddlewareKey] | None = None,
    ) -> None:
        self.strategy = strategy
        self.keys: list[CallableMiddlewareKey] = (
            ensure_list(keys) if keys else ensure_list(get_remote_address)
        )
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # just add the limit middleware to the request.state, the dependency on the 'APIRoute' takes care of the rest
        request.state.limiter = self
        response = await call_next(request)
        try:
            limit: "BaseLimiterDependency" = request.state.limit
            limit_keys: list[str] = request.state.limit_keys
        except AttributeError:
            return response
        if (
            limit.no_hit_status_codes
            and response.status_code in limit.no_hit_status_codes
        ):
            return response

        await self.strategy.hit(
            limit.item,
            *limit_keys,
        )
        return response
