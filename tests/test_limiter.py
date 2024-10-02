from time import sleep

from starlette.testclient import TestClient

from . import build_app


def test_limit_5_per_minute():
    app, routes = build_app()
    with TestClient(app) as client:
        assert client.get("/").status_code == 200
        assert client.get("/").status_code == 200
        assert client.get("/").status_code == 200
        assert client.get("/").status_code == 200
        assert client.get("/").status_code == 200
        assert client.get("/").status_code == 429  # 5/minute should be reached


def test_limits_1_per_second():
    app, routes = build_app()
    with TestClient(app) as client:
        assert client.post("/").status_code == 200
        sleep(0.5)
        assert client.post("/").status_code == 429
        sleep(0.5)
        assert client.get("/").status_code == 200


def test_limits_filters_hit():
    app, routes = build_app()
    with TestClient(app) as client:  # filter only apply if x-some-header == some-header
        assert (
            client.get("/other", headers={"x-some-header": "some-header"}).status_code
            == 200
        )
        assert (
            client.get("/other", headers={"x-some-header": "some-header"}).status_code
            == 200
        )
        assert (
            client.get("/other", headers={"x-some-header": "some-header"}).status_code
            == 200
        )
        assert (
            client.get("/other", headers={"x-some-header": "some-header"}).status_code
            == 429
        )


def test_limits_filters_nohit():
    app, routes = build_app()
    with TestClient(app) as client:  # filter only apply if x-some-header == some-header
        assert client.get("/other").status_code == 200
        assert client.get("/other").status_code == 200
        assert client.get("/other").status_code == 200
        assert client.get("/other").status_code == 200
        assert client.get("/other").status_code == 200
        assert client.get("/other").status_code == 200


def test_limits_shared_key():
    app, routes = build_app()
    with TestClient(app) as client:
        assert (
            client.get("/other", headers={"x-some-header": "some-header"}).status_code
            == 200
        )
        assert client.get("/shared").status_code == 200
        assert client.get("/shared").status_code == 200
        assert client.get("/shared").status_code == 429
        assert (
            client.get("/other", headers={"x-some-header": "some-header"}).status_code
            == 429
        )
