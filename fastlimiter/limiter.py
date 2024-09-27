import inspect
from typing import Any, Callable, ParamSpec, TypeVar

from fastapi import Depends
from fastapi.dependencies.utils import get_parameterless_sub_dependant
from fastapi.routing import APIRoute
from fastapi.utils import create_model_field
from limits import RateLimitItem, parse

from .dependencies import BaseLimiterDependency, _InjectedLimiterDependency
from .exceptions import _default_429_response
from .types import CallableFilter, CallableKey, SupportsRoutes
from .utils import create_response_model, find_api_route, get_api_routes

P = ParamSpec("P")
R = TypeVar("R")


def apply_limit(
    route: APIRoute,
    item: RateLimitItem,
    keys: CallableKey | list[CallableKey] | None,
    filters: CallableFilter | list[CallableFilter] | None,
    no_hit_status_codes: list[int] | None,
    default_response_model: dict[str, Any] | None,
    show_limit_in_response_model: bool,
) -> None:
    """Apply the limit to an `APIRoute` object

    Args:
        route (APIRoute): route to apply the limit to
        item (RateLimitItem): rate limit value
        keys (CallableKey | list[CallableKey] | None): a list of keys that identify a route or group of routes
        filters (CallableFilter | list[CallableFilter] | None): filters to check before hitting on a limit
        no_hit_status_codes (list[int] | None): response status codes that should not be count as a hit
        default_response_model (dict[str, Any] | None): default response model schema to show in docs
        show_limit_in_response_model (bool): should the value of rate limit be shown on the docs or not
    """
    if default_response_model is not None:
        route.responses[429] = default_response_model
        if (model := route.responses[429].get("model", None)) is not None:
            route.response_fields[429] = create_model_field(
                name=f"Response_429_{route.unique_id}",
                type_=create_response_model(model, item, show_limit_in_response_model),
            )
    # TODO: check if other limits were added previously
    dep_class = BaseLimiterDependency
    if filters or keys:
        dep_class = _InjectedLimiterDependency.apply_dependencies(keys, filters)
    limit_dependency = Depends(
        dep_class(
            limit_value=item,
            no_hit_status_codes=no_hit_status_codes,
        )
    )
    route.dependant.dependencies.insert(
        0,
        get_parameterless_sub_dependant(
            depends=limit_dependency,
            path=route.path_format,
        ),
    )


def limit(
    router: SupportsRoutes,
    limit_string: str,
    keys: CallableKey | list[CallableKey] | None = None,
    filters: CallableFilter | list[CallableFilter] | None = None,
    no_hit_status_codes: list[int] | None = None,
    default_response_model: dict[str, Any] | None = _default_429_response,
    show_limit_in_response_model: bool = True,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """A decorator function to apply limits to any route definition or group of routes.

    Note:
        You can use this function both as a decorator to apply limit to a route:

        ```py
        @limit(app, "5/minute")
        @app.get("/")
        def show_items(...):
            ...
        ```

        Or otherwise you can apply limits to a group of routes in a `APIRouter` object or `FastAPI` object:

        ```py
        router = APIRouter(prefix="/items")

        @router.get("/")
        def get_items(...):
            ...


        @router.post("/")
        def create_item(...):
            ...


        limit(router, "5/minute")
        ```

        In the second example the "5 per minute" limit will be applied to both `get_items` and `create_item` routes.

    Args:
        router (SupportsRoutes): An object that has `routes` attribute available with `router.routes` which ther routes are `APIRoute` objects. for example: `APIRouter` or `FastAPI` instances.
        limit_string (str): limit string in the format of {x}/{granularity}. for example: "5/minute" or "1/hour"
        keys (CallableKey | list[CallableKey] | None, optional): the unique keys to be used for this route. you can apply limits to routes using a shared key, all these routes limits will be calculated together. for example if you use the same keys for 'POST /items' and 'GET /items', rate limit will hit on that key with calling any of them.
        filters (CallableFilter | list[CallableFilter] | None, optional): Filters to check before counting a hit. It has to be a function or async function that returns a bool. a hit will be count if all of the filters return True. you can use Depends for filters and they will be resolved by FastAPI automatically.
        no_hit_status_codes (list[int] | None, optional): a list of status codes to not count a hit when they are returned. for example if you pass `[400, 404]`, if the response status code was in the list, a hit will not be counted.
        default_response_model (dict[str, Any] | None, optional): default response model to use for 429 responses in the autogenerated docs. if `None` was passed, nothing will be shown in the docs about this response.
        show_limit_in_response_model (bool, optional): Should the values for rate-limit be shown in the response model?

    Returns:
        Callable[[Callable[P, R]], Callable[P, R]] | None

    Note:
        This function returns a `Callable` if it was used as a decorator ('@' syntax) otherwise `None`.

    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        route = find_api_route(router, func)
        if route:
            apply_limit(
                route=route,
                item=parse(limit_string),
                keys=keys,
                filters=filters,
                no_hit_status_codes=no_hit_status_codes,
                default_response_model=default_response_model,
                show_limit_in_response_model=show_limit_in_response_model,
            )
        return func

    # check to see if this function was used as a decorator or not
    if ctx := inspect.stack()[1].code_context:
        if not ctx[0].startswith("@"):
            item = parse(limit_string)
            for route in get_api_routes(router):
                apply_limit(
                    route=route,
                    item=item,
                    keys=keys,
                    filters=filters,
                    no_hit_status_codes=no_hit_status_codes,
                    default_response_model=default_response_model,
                    show_limit_in_response_model=show_limit_in_response_model,
                )
            return  # type: ignore
    return decorator
