from fastapi import Depends, FastAPI
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
        pass

    @limit(app, "5/minute", keys="some_key")
    @app.post("/")
    async def _post():
        pass

    def some_dependency_function():
        return "huh a key"

    def some_funky_dependency() -> str:
        return "hellooo"

    async def some_filter_function(text: str = Depends(some_funky_dependency)) -> bool:
        if text == "hellooo":
            return True
        return False

    @limit(
        app,
        "5/minute",
        keys="some_key",
        filters=[some_filter_function, some_funky_dependency],
        override_default_keys=True,
    )
    @app.get("/")
    async def _other_get():
        pass

    @limit(
        app,
        "5/minute",
        keys=["some_key", some_dependency_function],
        filters=some_filter_function,
        override_default_keys=True,
    )
    @app.get("/")
    async def _other_second_get():
        pass

    # return app, [_get, _post, _other_get, _other_second_get]
    return app, list(get_api_routes(app))
