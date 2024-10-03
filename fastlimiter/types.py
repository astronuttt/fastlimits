from __future__ import annotations

from typing import Awaitable, Callable, TypeAlias, TypeVar

from fastapi import APIRouter, FastAPI, Request
from pydantic import BaseModel

SupportsRoutes: TypeAlias = APIRouter | FastAPI

ModelT = TypeVar("ModelT", bound=BaseModel)


CallableMiddlewareKey: TypeAlias = Callable[[Request], str | Awaitable[str]]

StrOrCallableKey: TypeAlias = str | Callable[..., str | Awaitable[str]]

CallableFilter: TypeAlias = Callable[..., bool | Awaitable[bool]]
