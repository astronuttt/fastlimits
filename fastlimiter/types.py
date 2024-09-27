from typing import Awaitable, Callable, TypeAlias, TypeVar

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel

SupportsRoutes: TypeAlias = APIRouter | FastAPI

ModelT = TypeVar("ModelT", bound=BaseModel)

StrOrCallableStr: TypeAlias = str | Callable[..., str]

CallableOrAwaitableCallable: TypeAlias = Callable[..., str | Awaitable[str]]

CallableKey: TypeAlias = Callable[..., str | Awaitable[str]]
CallableFilter: TypeAlias = Callable[..., bool | Awaitable[bool]]
