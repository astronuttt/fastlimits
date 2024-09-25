from fastapi import HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from limits import RateLimitItem
from pydantic import BaseModel


class RateLimitExceeded(HTTPException):
    """
    exception raised when a rate limit is hit.
    """

    limit = None

    def __init__(
        self,
        limit: RateLimitItem,
        status_code: int = status.HTTP_429_TOO_MANY_REQUESTS,
        detail: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.limit = limit
        super().__init__(
            status_code=status_code,
            detail=detail if detail else str(limit),
            headers=headers,
        )


class TooManyRequests(BaseModel):
    detail: str = "Rate limit exceeded: {x} per {y} {granularity}"


def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Build a simple JSON response that includes the details of the rate limit
    that was hit. If no limit is hit, the countdown is added to headers.
    """
    response = JSONResponse(
        {"error": f"Rate limit exceeded: {exc.detail}"}, status_code=exc.status_code
    )
    # inject retry_after header into Response
    return response
