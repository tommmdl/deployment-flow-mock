import pytest
from fastapi.testclient import TestClient

from app.main import add, create_app


@pytest.mark.parametrize("a,b,expected", [(2, 3, 5), (-2, 2, 0), (0.5, 1.5, 2)])
def test_add(a, b, expected):
    assert add(a, b) == expected


def test_lifecycle_and_contract():
    app = create_app()
    with TestClient(app) as client:
        assert client.get("/health/live").status_code == 200
        assert client.get("/health/ready").json() == {"ready": True}
        assert client.post("/api/calculate", json={"a": 2, "b": 3}).json() == {"result": 5}
        assert client.post("/api/calculate", json={"a": 1e13, "b": 0}).status_code == 422
        app.state.ready = False
        assert client.get("/health/ready").status_code == 503
        assert client.get("/health/live").status_code == 200
    assert app.state.ready is False


def test_metrics_no_unbounded_paths():
    with TestClient(create_app()) as client:
        for path in ["/missing/user1", "/missing/user2"]:
            assert client.get(path).status_code == 404
        client.post("/api/calculate", json={"a": 1, "b": 2})
        metrics = client.get("/metrics")
        assert "text/plain" in metrics.headers["content-type"]
        assert 'route="unmatched",status="404"} 2.0' in metrics.text
        assert "missing/user" not in metrics.text
        assert "http_request_duration_seconds_bucket" in metrics.text


def test_invalid_payload():
    with TestClient(create_app()) as client:
        assert client.post("/api/calculate", json={"a": "bad"}).status_code == 422
