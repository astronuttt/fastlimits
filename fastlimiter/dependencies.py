import asyncio
import inspect
from typing import Any, Sequence, Type

from fastapi import Depends, Request, Response
from limits import RateLimitItem, parse

from .exceptions import RateLimitExceeded
from .limiter import FastAPIRateLimiter
from .types import CallableFilter, CallableOrAwaitableCallable


# FastAPI dependency
class BaseLimiterDependency:
    """
    BaseLimiterDependency
    """

    def __init__(
        self,
        limit_value: str | RateLimitItem,
        key: str | None = None,
        no_hit_status_codes: list[int] | None = None,
    ) -> None:
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
        extra_keys: list[str] | None = None,
    ) -> Any:
        try:
            limiter: FastAPIRateLimiter = request.state.limiter
        except AttributeError:
            return
        keys = await self._build_key(limiter.key_funcs, request=request)
        if extra_keys:
            keys.extend(extra_keys)
        if not await limiter.strategy.test(self.item, *keys):
            raise RateLimitExceeded(limit=self.item)
        request.state.limit = self
        request.state.limit_keys = keys

    async def _build_key(
        self, key_funcs: Sequence[CallableOrAwaitableCallable], request: Request
    ) -> list[str]:
        _keys = [
            f(request) if not asyncio.iscoroutinefunction(f) else await f(request)
            for f in key_funcs
        ]
        if self.key:
            _keys.append(self.key)
        return _keys  # type: ignore


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
        extra_keys: list[str] | None = None,
        **filters: bool,
    ) -> Any:
        if all(filters.values()):
            return await super(type(self), self).__call__(request, response, extra_keys)

    @classmethod
    def apply_dependencies(
        cls, dependencies: CallableFilter | list[CallableFilter]
    ) -> Type["_InjectedLimiterDependency"]:
        dependencies = (
            [dependencies] if not isinstance(dependencies, list) else dependencies
        )
        dep_class = type(
            cls.__name__,
            cls.__bases__,
            dict(cls.__dict__),
        )
        sig = inspect.signature(dep_class.__call__)
        sig_params = tuple(sig.parameters.values())[:-1] + tuple(
            inspect.Parameter(
                f.__name__, inspect.Parameter.KEYWORD_ONLY, default=Depends(f)
            )
            for f in dependencies
        )
        dep_class.__call__.__signature__ = sig.replace(parameters=sig_params)
        return dep_class  # type: ignore
