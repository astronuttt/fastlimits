We have two knids of keys: 

- [Middleware level keys](#middlewarew-level-keys)   
    these keys will be applied to all of the endpoints (`Route`) or better say `limit items`


- [Endpoint level keys](#endpoint-level-keys)   
    thse keys are specific for each endpoint or `limit item`



## Middlewarew level keys


If we take a look at our (previous examples)[../getting-started/#keys], we notice that both of our routes has some keys in common:


take a look at `["127.0.0.1", "/", "get_items"]` and `["127.0.0.1", "/", "create_items"]`, the first two parts are the same. these are `Middleware` level keys.

we use `Middleware` level keys to distinguish each user from others.

for example we use the user's ip address here (`"127.0.0.1"`) as the first part of our keys. 

i sould note that there is no constraint here and you can use almost anything in the key functions. we used the `path` (`"/"`) for the second part here.


we can define middleware level keys when we setup our middleware, there are some pre-defined keys in the [Functions](../api-refrence/functions.md) but you can create your own functions as well and use them.


so lets create our own key function and use that in our middleware.

the only thing that matters when creating a custom key function is that it must get only one argument, and that argument is the `Request` object passed to it from the middleware. you can use any sync or async function based on your context.


all key fucntions must return a string, that string will be used as a key.


```py
def get_remote_port(request: Request) -> str:
    return request.client.port
```

and thats it! we now have a key function that distinguishes different users by their `ip address`!


now, if we want to use our key function, is as simple as this:

```py

from fastapi import FastAPI

from limits.aio.storage import MemoryStorage
from limits.aio.strategies import FixedWindowRateLimiter

from fastlimiter import RateLimitingMiddleware


app = FastAPI()

limiter = FixedWindowRateLimiter(storage=MemoryStorage())

app.add_middleware(
    RateLimitingMiddleware,
    limiter=limiter,
    keys=[get_remote_port] # just add the key function you want to this list, be careful not to add paranthesis at the end of function names
)
```

now if we check our limit item keys, instead of ip address from before, we get something like this:


`["55561", "get_items"]` or `["43541", "create_items"]` where `"55561"` and `"43541"` are different ports that requests came from.


this is dumb, right? usgin the port here is not useful at all, but lets see another example.

did you notice the ip from before was `127.0.0.1` and not a real ip address?

sometimes when our application is behind a reverse proxy, a cdn or something like that, we do not see the real ip of the user, 
     but sometimes when they forward the requests, they include the real ip of the user in a header.

guess what? we can use that header value as key!


```py
def get_real_ip(request: Request) -> str:
    return request.headers.get("X-Real-IP", None) or get_remote_address(request)
```

in this key function, we check for `X-Real-IP` header, if that does not exist, we fallback to the default `get_remote_address` function.



!!! note "Default key functions"
    by default the function applied is [get_remote_address](../api-refrence/functions.md/#fastlimiter.functions.get_remote_address).


!!! warning
    if you use `keys=` on the middleware, the functions you provided will be overridden to the default ones, so be careful when doing this.


## Endpoint level keys

If you notice, the second part in our limit items from previous example did not change when we updated our keys. and we still have `"get_items"` and `"create_items"` in our limit keys.


well that is because those are endpoint level keys. and by default the endpoint's function name will be used as a key for each item.

for example if we have an endpoint defined like this:

```py
@app.get("/")
async def get_items(...):
    ...
```

the `get_items` that is our function name will be used as a key by default.


well we also have the option to override these keys as well.


we do that by providing our key function to the `limit` decorator.


### Key functions


key functions are, deep down, `dependencies`, so you can use `Depends` in them!


we can write an endpoint level key function like this:

```py
def get_user_id(user: User = Depends(get_current_user)) -> str:
    return str(user.id)


@limit(app, "5/minute", keys=[get_user_id], override_default_keys=True)
@app.get("/")
async def get_items(...):
    ...
```

now let's take a look at our limit key:

`["127.0.0.1", "1"]`


the `override_default_keys` argument will remove default endpoint level keys and add only our provided keys to the limit item.

if we was to pass False, for example `override_default_keys=False`, our limit key would be `["127.0.0.1", "get_items", "1"]`.



### Key strings

just like how we provided key functions to our limit decorator, we can use strings for the keys. 

```py
@limit(app, "5/minute", keys=["some_string"], override_default_keys=True)
@app.get("/")
async def get_items(...):
    ...
```

and now if we check our our limit key, it will be something like `["127.0.0.1", "some_string"]`.

where is this useful? well one useful usage of this will be when you want to create limit two or more endpoints together.


```py
@limit(app, "5/minute", keys=["some_string"], override_default_keys=True)
@app.get("/")
async def get_items(...):
    ...

@limit(app, "5/minute", keys=["some_string"], override_default_keys=True)
@app.post("/")
async def create_items(...):
    ...
```

now we bound these two endpoints together. if the user calls the first endpoint, 2 times, and second one 3 times, we have 5 in total and our limit would be filled and they can't use any of these two endpoints anymore.


### Key functions + Key strings

You also have the option to combine strings and functions together to create more specialized limit keys.


```py
@limit(app, "5/minute", keys=[some_key_function, "some_key_string"])
```

!!! note "The order matters"
    be careful when adding multiple keys because the order of keys matter!

    `["127.0.0.1", "first", "second"]` and `["127.0.0.1", "second", "first"]` are two completly different items.
