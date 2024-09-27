import asyncio
import inspect
from typing import TYPE_CHECKING, Any, Self, Sequence, Type

from fastapi import Depends, Request, Response
from limits import RateLimitItem, parse

from .exceptions import RateLimitExceeded
from .types import CallableFilter, CallableKey, CallableOrAwaitableCallable
from .utils import ensure_list, fncopy

if TYPE_CHECKING:
    from .middleware import RateLimitingMiddleware


# FastAPI dependency
class BaseLimiterDependency:
    """
    This dpendency will be injected into the `APIRoute` object and does the actual 'limiting' job.
    """

    def __init__(
        self,
        limit_value: str | RateLimitItem,
        key: str | None = None,
        no_hit_status_codes: list[int] | None = None,
    ) -> None:
        """BaseLimiterDependency

        Args:
            limit_value (str | RateLimitItem): a string like "5/minute" or a `RateLimitItem` object
            key (str | None, optional): A key that can be shared between multiple routes for grouping them, or seperating them.
            no_hit_status_codes (list[int] | None, optional): the response statuses that won't be count as a hit on the limiter.
        """
        if isinstance(limit_value, str):
            self.item = parse(limit_value)
        else:
            self.item = limit_value
        self.key = key
        self.no_hit_status_codes = no_hit_status_codes if no_hit_status_codes else []

    async def __call__(
        self,
        request: Request,
        response: Response,
        keys: list[str] | None = None,
    ) -> None:
        """The actual callable that FastAPI call and checks for rate-limiting

        Args:
            request (Request): request object from FastAPI
            response (Response): response object from FastAPI
            keys (list[str] | None, optional): extra keys other than those provided by the middleware as identifiers for a rate-limit item

        Raises:
            RateLimitExceeded: when the rate limit exceeds the allowed value
        """
        try:
            limiter: "RateLimitingMiddleware" = request.state.limiter
        except AttributeError:
            return
        built_keys = await self._build_key(limiter.key_funcs, request=request)
        if keys:
            built_keys.extend(keys)
        if not await limiter.strategy.test(self.item, *built_keys):
            raise RateLimitExceeded(
                limit=self.item, detail=f"Rate limit exceeded: {self.item}"
            )
        request.state.limit = self
        request.state.limit_keys = built_keys

    async def _build_key(  # TODO: make key_funcs be dependencies as well?
        self, key_funcs: Sequence[CallableOrAwaitableCallable], request: Request
    ) -> list[str]:
        """Build an identifier for a rate-limit item

        Args:
            key_funcs (Sequence[CallableOrAwaitableCallable]): a list of keys passed to the `RateLimitingMiddleware` and the dependency itself. these keys will form a identifier for a limit item.
            request (Request): this has to be changed so keys will also work with Depends

        Returns:
            list[str]: a list containing string keys from the provided callables
        """
        _keys = [
            f(request) if not asyncio.iscoroutinefunction(f) else await f(request)
            for f in key_funcs
        ]
        if self.key:
            _keys.append(self.key)
        return _keys  # type: ignore


def filters_resolver(**filters: bool) -> dict[str, bool]:
    return filters


def keys_resolver(**keys: str) -> list[str]:
    return list(keys.values())


class _InjectedLimiterDependency(BaseLimiterDependency):
    """
    A modified version of this class will be injected into the
        `APIRoute` dependencies to trick FastAPI to resolve the dependencies inside of the functions passed from
        filter argument of `limit` decorator.
    """

    async def __call__(
        self,
        request: Request,
        response: Response,
        keys: list[str],
        filters: dict[str, bool],
    ) -> Any:
        if all(filters.values()):
            return await super(type(self), self).__call__(request, response, keys)

    @classmethod
    def apply_dependencies(
        cls,
        keys: CallableKey | list[CallableKey] | None,
        filters: CallableFilter | list[CallableFilter] | None,
    ) -> Type[Self]:
        """Applies the filters and keys provided by the caller to a modified version of this class and returns it

        Returns:
            Type[_injectedLimiterDependency]:
        """
        if not keys and not filters:
            return cls  # do not change anything

        dep_class = type(
            cls.__name__,
            cls.__bases__,
            dict(cls.__dict__),
        )

        # create a copy of resovler functions and change their signature to add keys and filters as dependencies for FastAPI to pick up
        _keys_resolver = keys_resolver
        _filters_resolver = filters_resolver
        keys = ensure_list(keys)
        filters = ensure_list(filters)
        _keys_resolver = fncopy(
            keys_resolver,
            sig=tuple(
                inspect.Parameter(
                    k.__name__, inspect.Parameter.KEYWORD_ONLY, default=Depends(k)
                )
                for k in keys
            ),
        )
        _filters_resolver = fncopy(
            filters_resolver,
            sig=tuple(
                inspect.Parameter(
                    f.__name__, inspect.Parameter.KEYWORD_ONLY, default=Depends(f)
                )
                for f in filters
            ),
        )

        sig = inspect.signature(dep_class.__call__)

        sig_params = tuple(sig.parameters.values())[:-2] + tuple(
            (
                inspect.Parameter(
                    "keys",
                    inspect.Parameter.KEYWORD_ONLY,
                    default=Depends(_keys_resolver),
                ),
                inspect.Parameter(
                    "filters",
                    inspect.Parameter.KEYWORD_ONLY,
                    default=Depends(_filters_resolver),
                ),
            )
        )
        dep_class.__call__.__signature__ = sig.replace(parameters=sig_params)
        return dep_class  # type: ignore
