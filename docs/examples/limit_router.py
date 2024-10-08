from fastapi import APIRouter, FastAPI
from limits.aio.storage import MemoryStorage
from limits.aio.strategies import FixedWindowRateLimiter

from fastlimits import RateLimitingMiddleware, limit

app = FastAPI()

limiter = FixedWindowRateLimiter(storage=MemoryStorage())

app.add_middleware(
    RateLimitingMiddleware,
    strategy=limiter,
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


router = APIRouter(prefix="/user")


@limit(router, "10/hour")
@router.get("/")
async def get_user(user: User = ...):
    return {"user": ...}


@limit(router, "1/minute")
@router.post("/")
async def create_user(create_user: UserCreateSchema):
    return {"user": create_user}


app.include_router(router)
