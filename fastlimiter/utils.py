from typing import Any, Callable

from fastapi.routing import APIRoute
from limits import RateLimitItem
from pydantic import create_model

from .types import ModelT, SupportsRoutes


def find_api_route(router: SupportsRoutes, func: Callable[..., Any]) -> APIRoute | None:
    """Find the APIRoute object from the APIRouter.routes or FastAPI.routes"""
    route = None
    for r in router.routes:
        if isinstance(r, APIRoute) and getattr(r, "endpoint", None) == func:
            route = r
            break
    return route


def create_response_model(
    model: type[ModelT],
    parsed_limit: RateLimitItem,
    show_limit_in_response_model: bool = False,
) -> type[ModelT]:
    """
    Returns a copy of the model with the default value updated and placeholders filled.
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
