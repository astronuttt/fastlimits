from fastapi import FastAPI
from limits.aio.storage import MemoryStorage
from limits.aio.strategies import FixedWindowRateLimiter

from fastlimits import RateLimitingMiddleware, limit

app = FastAPI()

limiter = FixedWindowRateLimiter(storage=MemoryStorage())

app.add_middleware(
    RateLimitingMiddleware,
    strategy=limiter,
)


@limit(app, "5/minute")
@app.get("/")
async def root():
    return {"message": "Hello World"}
