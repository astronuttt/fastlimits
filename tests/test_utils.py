from fastapi import FastAPI

from fastlimiter import utils


def test_find_api_route():
    app = FastAPI()

    @app.get("/")
    async def _get(): ...

    route = utils.find_api_route(app, _get)
    assert route


def test_get_api_routes():
    app = FastAPI()

    @app.get("/")
    async def _get(): ...

    @app.post("/")
    async def _post(): ...

    @app.get("/someroute")
    async def _other_get(): ...

    assert [r.endpoint for r in utils.get_api_routes(app)] == [_get, _post, _other_get]


def test_ensure_list():
    assert [] == utils.ensure_list([])
    assert [] == utils.ensure_list(None)
    assert [1, 2, 3] == utils.ensure_list([1, 2, 3])
    assert ["somestr"] == utils.ensure_list("somestr")
