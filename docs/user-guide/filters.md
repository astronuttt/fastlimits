Filters are nice addition to keys. but they are different from each other and do completly different things.

as we said before, Keys are what distinguish each endpoint, or each user from each other.

a combination of Keys will create a `limit item` and that limit item is what we check for rate limiting.


Filters on the other hand, are conditions that we check to see if we should count a `Hit` or not.


let's explain with a simple example:


we have two user levels: admins and normal users.

```py
# first lets define our roles
class Role(enum.Enum):
    admin = "admin"
    user = "user"

# and we create a user class for the sake of this example
class User(BaseModel):
    username: str
    email: str

    role: Role
```

what if we want to define different kind of limits for each role. for example 10 request per minute for normal users, but no limits for admin users.

this is where filters come handy.

we can create a filter that checks and finds normal users before we apply limits:

```py
def filter_not_admin(user: User = Depends(get_current_user)) -> bool:
    return user.role != Role.admin
```

and thats it! now we can use this filter in our endpoints:

```py
@limit(app, "10/minute", filters=filter_not_admin)
@app.get("/")
async def get_some_resource(user: User = Depends(get_current_user)):
    ...
```

and done! neat right?

now if a normal user calls this endpoint more than 10 times per minute, they will be banned. but an admin user can call as much as they want.


you can even define seperate limits for this two roles:


```py
@limit(app, "10/minute", filters=filter_not_admin)
@limit(app, "100/minute")
@app.get("/")
async def get_some_resource(user: User = Depends(get_current_user)):
    ...
```

The limits are processed top to bottom, so if the filters of first limit will satisfy (user is not an admin), the second one would not be processed.

and the opposite of this works too. if the first limit's filters would not return `True` (the user is an admin), the second one would be hit.


!!! warning

    be careful when combining multiple limits together, they might cause unwanted outcomes if you don't order them properly!