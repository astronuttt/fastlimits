from __future__ import annotations

import inspect
import types
from typing import Any, Callable, Generator, TypeVar

from fastapi.routing import APIRoute
from limits import RateLimitItem
from pydantic import create_model

from .types import ModelT, SupportsRoutes

P = TypeVar("P")
R = TypeVar("R")


def get_api_routes(router: SupportsRoutes) -> Generator[APIRoute, None, None]:
    """Generator that yields `APIRoute` objects from an `APIRouter`

    Args:
        router (SupportsRoutes): router object, can be `APIRouter` or `FastAPI`

    Yields:
        Generator[APIRoute, None, None]: the `APIRoute` object
    """
    yield from (r for r in router.routes if isinstance(r, APIRoute))


def find_api_route(router: SupportsRoutes, func: Callable[..., Any]) -> APIRoute | None:
    """Find the APIRoute object from the APIRouter.routes or FastAPI.routes"""
    for r in get_api_routes(router):
        if getattr(r, "endpoint", None) == func:
            return r


def create_response_model(
    model: type[ModelT],
    parsed_limit: RateLimitItem,
    show_limit_in_response_model: bool = False,
) -> type[ModelT]:
    """
    Returns a copy of the model with the default value updated and placeholders filled.G
    """
    _model = model
    if show_limit_in_response_model:
        if (detail := model.model_fields.get("detail", None)) is not None:
            _detail = detail.default.format(
                x=parsed_limit.amount,
                y=parsed_limit.multiples,
                granularity=parsed_limit.GRANULARITY.name,
            )
            _model = create_model(
                model.__name__,
                __base__=model,
                detail=(str, _detail),
            )
    return _model


def fncopy(
    func: Callable[..., R], sig: tuple[inspect.Parameter, ...]
) -> Callable[..., R]:
    """creates a deepcopy of a function with the same code, globals, defaults, closures but slighlty different signature

    Args:
        func (Callable[P, R]): the function to create a copy of
        sig (tuple[inspect.Parameter]): new parameters

    Returns:
        Callable[P, R]: the copied new function
    """
    fn = types.FunctionType(
        func.__code__,
        func.__globals__,
        func.__name__,
        func.__defaults__,
        func.__closure__,
    )
    fn.__dict__.update(func.__dict__)
    fn.__signature__ = inspect.Signature(parameters=sig)  # type: ignore
    return fn


def ensure_list(value: P | list[P] | None) -> list[P]:
    """ensure the value is a list

    returns an empty list if value is None
    """
    if not value:
        return []
    if isinstance(value, list):
        return value
    return [value]
