from limits.aio.storage import MemoryStorage
from limits.aio.strategies import FixedWindowRateLimiter, RateLimiter
from limits.storage import StorageTypes

from .functions import get_remote_address
from .types import CallableOrAwaitableCallable


class FastAPIRateLimiter:
    """Wrapper/container around limits.RateLimiter to add some fastapi related functionality"""

    def __init__(
        self,
        storage: StorageTypes | None = None,
        strategy: RateLimiter | None = None,
        key_funcs: list[CallableOrAwaitableCallable] | None = None,
    ) -> None:
        if not storage:
            storage = MemoryStorage()
        self.storage = storage
        if not strategy:
            strategy = FixedWindowRateLimiter(storage=self.storage)
        self.strategy = strategy
        self.key_funcs = key_funcs if key_funcs else [get_remote_address]
