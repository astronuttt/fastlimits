There are a couple of things you should know before we get started.

There are only few concepts that you should know about. [Hit](#hit), [Filters](#filters) and [Keys](#keys).


### Hit

Each time a request comes in, some conditions will be checked and if those conditions were met, a `hit` will be count for that limit item.

take a look at this simple example:

```py
@limit(app, "5/minute")
@app.get("/")
async def items(...):
    ...
```

for this very simple example, the only condition that applies is the `path` (`"/"`) and the provided keys to the middleware that distinguish each user.

by default each user will be identified by their ip addresses.

so the key for this request will be something like:

```py
["127.0.0.1", "/", "items"]
```

we call this combination of strings, a `limit item`.


everytime we encounter a key like this, we will count a `Hit` for that limit item.

!!! note

    we go into more details about keys later at [Keys](#keys).


and in this context, if the user sends more than 5 requests to that key in less than a minute, they will get a '429 TOO Many Requests' response.



It gets a little more complex than this in the real world. what if we want to apply limits based on users roles?

take this, we want `'admin'` users to be able to call the `"/"` endpoint 100 times per minute, but `'normal'` users could only do 10 per minute.

this is where [Filters](#filters) come in.

### Filters

What are filters? as the name suggest, they filter out requests based on provided data 
and if all the filters say 'True', the limit item will be applied and a `Hit` will be calculated.

filters can be any callable, [they can be async or sync](https://fastapi.tiangolo.com/tutorial/dependencies/#to-async-or-not-to-async), they can even contain a [dependency](https://fastapi.tiangolo.com/tutorial/dependencies/). but they must return a `bool`.


here's a simple example:

```py
def filter_not_admins(user: User = Depends(get_current_user)) -> bool:
    if user.role != "admin":
        return True
    return False
```

now we have a filter and we can use it in our limit item:

```py
@limit(app, "5/minute", filters=filter_not_admins)
@app.get("/")
async def items(user: User = Depends(get_current_user)):
    ...
```

and thats it! now our limit only works when the user is not an `admin`. 


!!! note

    Do not worry about the use of `get_current_user` if you used it multiple times like our example here, `FastAPI` will cache dependencies and `get_current_user` will be called only once!


!!! note "More about filters"
    You can learn more about Filters [here](../filters)



now we can go one step forward and add more conditions to our limits, group our limits together and much more.


### Keys

Keys are essentially the thing that make a `limit item` distinguishable from others. lets take another look at our example from before:

```py
@limit(app, "5/minute")
@app.get("/")
async def get_items(...):
    ...


@limit(app, "5/minute")
@app.post("/")
async def create_items(...):
    ...
```

lets say we want to limit this two endpoints together, any hit on `get_items` will be the same as a hit on `create_items`.

what i mean by this is that if the user calls the `get_items` 3 times, and `create_items` 2 times, we have 5 in total and the user should be limited.

by default the keys for this two endpoints are different. for example:

get_items:

```py
["127.0.0.1", "/", "get_items"]
```

create_items:
```py
["127.0.0.1", "/", "create_items"]
```

and as we said before, these are two different keys and are calculated seperately. 

but we can get around this by using the `keys=` argument from the `limit`!


```py
@limit(app, "5/minute", keys="items")
@app.get("/")
async def get_items(...):
    ...


@limit(app, "5/minute", keys="items")
@app.post("/")
async def create_items(...):
    ...
```


so now the keys to both of this endpoints will be `["127.0.0.1", "/", "items"]` and they will be treaded as they are the same endpoint!


!!! warning

    be carefull when doing this! the limit on both of this endpoints must match, for example here both are `"5/minute"`, the library does not constraint you from doing otherwise but unwanted conditions might occur!



!!! note "More about keys"
    You can learn more about Keys [here](../keys)



You can do almost anything by combining Keys and Filters together. you can learn more about these in their respective chapters.