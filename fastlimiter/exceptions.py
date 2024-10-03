from typing import Dict, Optional

from fastapi import HTTPException, status
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
        detail: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.limit = limit
        # TODO: calculate retry_after and add it to the headers
        super().__init__(
            status_code=status_code,
            detail=detail if detail else str(limit),
            headers=headers,
        )


class TooManyRequests(BaseModel):
    detail: str = "Rate limit exceeded: {x} per {y} {granularity}"


_default_429_response = {
    "model": TooManyRequests,
    "headers": {
        "retry_after": {"description": "Retry after n seconds", "type": "integer"}
    },
}
