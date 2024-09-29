import inspect

from fastapi import FastAPI
from fastapi.dependencies.models import Dependant

from fastlimiter import dependencies, limit
from fastlimiter.utils import find_api_route

app = FastAPI()


@limit(app, "5/minute")
@app.get("/")
async def _get():
    pass


@limit(app, "5/minute", keys="some_key")
@app.post("/")
async def _post():
    pass


@limit(app, "5/minute", keys="some_key", override_default_keys=True)
@app.get("/")
async def _other_get():
    pass


def some_dependency_function():
    return "huh a key"


@limit(
    app,
    "5/minute",
    keys=["some_key", some_dependency_function],
    override_default_keys=True,
)
@app.get("/")
async def _other_second_get():
    pass


def get_limit_dependency(_deps: list[Dependant]) -> Dependant | None:
    for dep in _deps:
        if issubclass(type(dep.call), dependencies.BaseLimiterDependency):
            return dep


def test_dependency_injector():
    route = find_api_route(app, _get)
    assert route
    dep = get_limit_dependency(route.dependant.dependencies)

    # check if dependency was injected
    assert dep is not None

    # check if keys_resovlers and filters_resovler sub dependencies were injected too
    sub_deps = [sub_dep.name for sub_dep in dep.dependencies]
    assert "keys" in sub_deps
    assert "filters" in sub_deps


def test_dependency_keys_default():
    route = find_api_route(app, _get)
    assert route
    dep = get_limit_dependency(route.dependant.dependencies)
    assert dep is not None
    key_resolver = None
    for sd in dep.dependencies:
        if sd.name == "keys":
            key_resolver = sd

    assert key_resolver is not None

    sig = inspect.signature(key_resolver.call)
    assert ["_get"] == list(p.name for p in sig.parameters.values())


def test_dependency_keys_added_str():
    route = find_api_route(app, _post)
    assert route
    dep = get_limit_dependency(route.dependant.dependencies)
    assert dep is not None
    key_resolver = None
    for sd in dep.dependencies:
        if sd.name == "keys":
            key_resolver = sd

    assert key_resolver is not None

    sig = inspect.signature(key_resolver.call)
    assert ["_post", "some_key"] == list(p.name for p in sig.parameters.values())


def test_dependency_keys_override_default():
    route = find_api_route(app, _other_get)
    assert route
    dep = get_limit_dependency(route.dependant.dependencies)
    assert dep is not None
    key_resolver = None
    for sd in dep.dependencies:
        if sd.name == "keys":
            key_resolver = sd

    assert key_resolver is not None

    sig = inspect.signature(key_resolver.call)
    assert ["some_key"] == list(p.name for p in sig.parameters.values())


def test_dependency_keys_add_function():
    route = find_api_route(app, _other_second_get)
    assert route
    dep = get_limit_dependency(route.dependant.dependencies)
    assert dep is not None
    key_resolver = None
    for sd in dep.dependencies:
        if sd.name == "keys":
            key_resolver = sd

    assert key_resolver is not None

    sig = inspect.signature(key_resolver.call)
    assert ["some_key", "some_dependency_function"] == list(
        p.name for p in sig.parameters.values()
    )
