The thing that will be put between our application and limiting logic is our `Middleware`.


our limiting logic won't work without this piece and has no way to intercept incoming requests.

!!! note "FastAPI Middlewares"

    you can read more about middlewares in FastAPI's documentation from <a href="https://fastapi.tiangolo.com/tutorial/middleware/" target="_blank">here</a>.


First of all, we have to setup our middleware, we also need some stuff from our backend library <a href="https://github.com/alisaifee/limits" target="_blank">limits</a>. we will go into more details about these later.


```py

from fastapi import FastAPI

from limits.aio.storage import MemoryStorage
from limits.aio.strategies import FixedWindowRateLimiter

from fastlimiter import RateLimitingMiddleware


# create our fastapi app

app = FastAPI()

# create our limiter object

limiter = FixedWindowRateLimiter(storage=MemoryStorage())

# add our middleware to our fastapi app

app.add_middleware(
    RateLimitingMiddleware,
    strategy=limiter,
)
```

And thats it! our setup is Done, now we can start adding limits to our endpoints.

but first, let's breakdown some parts and explain a little more.


The `limits` library supports multiple storage and strategies to use, we used the simples storage that is `MemoryStorage` and does not need anything to be installed and works out of the box.


for the strategy, we used `FixedWindowRateLimiter` that has the least overhead and meets the needs of most applications. but you are free to use anything that `limits` library supports!


!!! note "More Storages"
    If you want to know more about different storage backends supported you can refer to limits documentation <a href="https://limits.readthedocs.io/en/latest/storage.html" target="_blank">here</a>.


!!! note "More Strategies"
    If you want to know more about different strategies supported you can refer to limits documentation <a href="https://limits.readthedocs.io/en/latest/strategies.html" target="_blank">here</a>.