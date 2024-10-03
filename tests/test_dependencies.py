import inspect
from typing import List, Optional

from fastapi.dependencies.models import Dependant

from fastlimits import dependencies

from . import build_app


def get_limit_dependency(_deps: List[Dependant]) -> Optional[Dependant]:
    for dep in _deps:
        if issubclass(type(dep.call), dependencies.BaseLimiterDependency):
            return dep


def test_dependency_injector():
    app, routes = build_app()

    for route in routes:
        dep = get_limit_dependency(route.dependant.dependencies)

        # check if dependency was injected
        assert dep is not None

        # check if keys_resovlers and filters_resovler sub dependencies were injected too
        sub_deps = [sub_dep.name for sub_dep in dep.dependencies]
        assert "keys" in sub_deps
        assert "filters" in sub_deps


def test_dependency_keys_inject():
    app, routes = build_app()
    for route in routes:
        dep = get_limit_dependency(route.dependant.dependencies)
        assert dep is not None
        key_resolver = None
        for sd in dep.dependencies:
            if sd.name == "keys":
                key_resolver = sd

        assert key_resolver is not None

        sig = inspect.signature(key_resolver.call)
        name = route.endpoint.__name__
        if name == "_get":
            keys = ["_get"]
        elif name == "_post":
            keys = ["_post", "some_key"]
        elif name == "_other_get":
            keys = ["some_key"]
        elif name == "_other_second_get":
            keys = ["some_key", "some_dependency_function"]
        else:
            continue
        assert keys == list(p.name for p in sig.parameters.values())


def test_dependency_filters_inject():
    app, routes = build_app()
    for route in routes:
        dep = get_limit_dependency(route.dependant.dependencies)
        assert dep is not None
        filters_resolver = None
        for sd in dep.dependencies:
            if sd.name == "filters":
                filters_resolver = sd

        assert filters_resolver is not None

        sig = inspect.signature(filters_resolver.call)
        name = route.endpoint.__name__
        if name == "_other_get":
            filters = ["some_filter_function", "some_funky_dependency"]
        elif name == "_other_second_get":
            filters = ["some_filter_function"]
        else:
            filters = []
        assert filters == list(p.name for p in sig.parameters.values())
