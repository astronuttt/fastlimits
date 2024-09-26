Why and how FastLimiter works


There are some good libraries out there that do the same job as FastLimiter but each of them lack 
some very needed functionality.

for example there is no simple way to apply limits based on the role of a user.

Suppose that we want to set limit for 'admin' users as 100 per minute, but 10 per minute for 'normal users'.

if you followed the <a href="https://fastapi.tiangolo.com/tutorial/security/get-current-user/" target="_blank">FastAPI documentation</a> and have for example a `get_current_user` dependency, why not use that to get the current user? and this is the exact reasoning behind how FastLimiter works, by injecting dependencies.


you'll get to know more about how to setup and use FastLimiter in the next chapter.