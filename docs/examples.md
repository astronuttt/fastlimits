## Simple example


```python linenums="1" hl_lines="2 3 5 9 11-14 17"
--8<-- "docs/examples/limit_simple.py"
```



## Apply limits to all routes (Default limit)


```python linenums="1" hl_lines="2 3 5 9 11-14 22"
--8<-- "docs/examples/limit_all_routes.py"
```


## Limits on router object

```python linenums="1" hl_lines="2 3 5 9 11-14 25 31"
--8<-- "docs/examples/limit_router.py"
```


## Limit based on dependencies

examples taken from <a href="https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/" target="_blank">FastAPI documentation</a>.

```python linenums="1" hl_lines="8 9 13 59 61-64 129-132 135 154 162"
--8<-- "docs/examples/limit_with_security.py"
```