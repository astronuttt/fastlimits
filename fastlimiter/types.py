from typing import Awaitable, Callable, TypeVar, Union

from fastapi import APIRouter, FastAPI, Request
from pydantic import BaseModel
from typing_extensions import TypeAlias

SupportsRoutes: TypeAlias = Union[APIRouter, FastAPI]

ModelT = TypeVar("ModelT", bound=BaseModel)


CallableMiddlewareKey: TypeAlias = Callable[[Request], Union[str, Awaitable[str]]]

StrOrCallableKey: TypeAlias = Union[str, Callable[..., Union[str, Awaitable[str]]]]

CallableFilter: TypeAlias = Callable[..., Union[bool, Awaitable[bool]]]
