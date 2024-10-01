<p align="center">
[WIP] <em>FastLimiter is a rate limiting extension/middleware for <a href="https://github.com/fastapi/fastapi" target="_blank">FastAPI</a> applications powered by <a href="https://github.com/alisaifee/limits" target="_blank">limits</a>.</em>
</p>

---

**Documentation**: <a href="https://astronuttt.github.io/fastlimiter" target="_blank">https://astronuttt.github.io/fastlimiter</a>

**Source Code**: <a href="https://github.com/astronuttt/fastlimiter" target="_blank">https://github.com/astronuttt/fastlimiter</a>


## Features

* **FastAPI depencies support**: FastAPI dependencies can be used in limiters to apply limits based on the injected dependency.

* **Automatic documentation for additional responses**: It will automatically add additional `429_TOO_MANY_REQUESTS` response to the schema, so it can be used in the generated documentation.

* **Middlewares support**: Can act as a middleware to apply limits to all the routes and etc.

* **Partial and full limits**: limits can be applied to an `APIRouter` the whole `FastAPI` app or a single route operation.

* **Exclude certain responses**: certain responses can be excluded from the limitation. for example, you can exclude `400` status codes and if the route returns a `400` it won't be counted for limitations.

* **Limit groups**: You can apply a group of limits, for example a certain limit for admin users, and a certain limit for normal users.

* **Multiple limit strategies**: It uses the <a href="https://github.com/alisaifee/limits" target="_blank">limits</a> library on the back-end so it supports multiple strategies. see <a href="https://github.com/alisaifee/limits?tab=readme-ov-file#supported-strategies" target="_blank">Supported Strategies</a>.

* **Multiple Storage backends**: As another perk of the <a href="https://github.com/alisaifee/limits" target="_blank">limits</a> library, multiple storage backends are supported. see <a href="https://github.com/alisaifee/limits?tab=readme-ov-file#storage-backends" target="_blank">Storage backends</a>


## How it works

It uses the <a href="https://github.com/alisaifee/limits" target="_blank">limits</a> library in the backend for all the limitation handlings.

As for the `FastAPI` side it Injects a dependency into the `APIRoute` object and that dependency acts as the main component for limitation on that route. one of it's perks are that you can apply some limitations based on a `Depends` and everything will be handled automatically by `FastAPI`.


## Other limit libraries

Some of the ideas for this library comes from two great libraries that were created before this:

SlowApi: <a href="https://github.com/laurents/slowapi" target="_blank">https://github.com/laurents/slowapi</a>

fastapi-limiter: <a href="https://github.com/long2ice/fastapi-limiter" target="_blank">https://github.com/long2ice/fastapi-limiter</a>


These are two great libraries, but each of them lack some functionality, so I decided to extend them and create FastLimiter.


## Quick Start

This library works by a combination of a dependency and a middleware, but using it is very simple.

First step is to setup the `Limiter` and then add the limiting middleware to your `FastAPI` application.


```python
from fastapi import FastAPI

# The simplest setup is to use 'MemoryStorage' and 'FixedWindowRateLimiter', you don't even have to specify these because it's the default
from limits.aio.storage import MemoryStorage
from limits.aio.strategies import FixedWindowRateLimiter

from fastlimiter import RateLimitingMiddleware, limit


app = FastAPI()


limiter = FixedWindowRateLimiter(storage=MemoryStorage())
app.add_middleware(RateLimitingMiddleware, strategy=limiter)

# and thats for the setup! you can now use the 'limit' decorator to apply limits on any route

@limit(app, "5/minute")
@app.get("/")
async def items(q: int | None = None):
    return {"q": q}
```

And thats it! now users can call the GET 'items' route only 5 times per minute.


For more usage please refer to the documentation at <a href="https://astronuttt.github.io/fastlimiter" target="_blank">https://astronuttt.github.io/fastlimiter</a>


---

This library inherits most of it's functionality from <a href="https://github.com/alisaifee/limits" target="_blank">limits</a>. special thanks to the everyone who helped make that happen.


## License

This project is licensed under the terms of the MIT license.