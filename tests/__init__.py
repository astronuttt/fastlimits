from fastapi import Depends, FastAPI, Header
from fastapi.routing import APIRoute
from limits.aio.storage import MemoryStorage
from limits.aio.strategies import FixedWindowRateLimiter

from fastlimiter import RateLimitingMiddleware, limit
from fastlimiter.utils import get_api_routes


def build_app() -> tuple[FastAPI, list[APIRoute]]:
    app = FastAPI()

    limiter = FixedWindowRateLimiter(storage=MemoryStorage())

    app.add_middleware(
        RateLimitingMiddleware,
        strategy=limiter,
    )

    @limit(app, "5/minute")
    @app.get("/")
    async def _get():
        return

    @limit(app, "1/second", keys="some_key")
    @app.post("/")
    async def _post():
        return

    def some_dependency_function():
        return "huh a key"

    def some_funky_dependency() -> str:
        return "hellooo"

    async def some_filter_function(
        text: str = Depends(some_funky_dependency),
        x_some_header: str = Header("not-some-header"),
    ) -> bool:
        if x_some_header == "some-header":
            return True
        return False

    @limit(
        app,
        "3/minute",
        keys="some_key",
        filters=[some_filter_function, some_funky_dependency],
        override_default_keys=True,
    )
    @app.get("/other")
    async def _other_get():
        return

    @limit(
        app,
        "3/minute",
        keys="some_key",
        override_default_keys=True,
    )
    @app.get("/shared")
    async def _shared():
        return

    @limit(
        app,
        "3/minute",
        keys=["some_key", some_dependency_function],
        filters=some_filter_function,
        override_default_keys=True,
    )
    @app.get("/second")
    async def _other_second_get():
        return

    # return app, [_get, _post, _other_get, _other_second_get]
    return app, list(get_api_routes(app))
