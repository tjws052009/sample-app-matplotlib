import pytest
from fastapi.testclient import TestClient

from app.main import app, ledger


@pytest.fixture(autouse=True)
def clean_ledger():
    ledger.reset()
    yield
    ledger.reset()


@pytest.fixture
def client():
    return TestClient(app)


def test_page_describes_total_sales(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Total sales" in response.text
    assert "Start recording" in response.text


def test_plot_endpoint_returns_svg(client):
    response = client.get("/plot.svg")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")
    assert b"<svg" in response.content
    assert b'width="100%"' in response.content


def test_recording_pause_and_clear(client):
    started = client.post("/api/start")
    assert started.status_code == 200
    body = started.json()
    assert body["count"] == 12
    assert body["running"] is True
    assert body["latest"] > body["points"][0]["y"]
    assert body["library"]["source"].endswith("matplotlib_test")
    assert body["library"]["version"]

    paused = client.post("/api/pause").json()
    assert paused["status"] == "paused"
    assert paused["count"] == 12

    resumed = client.post("/api/resume").json()
    assert resumed["running"] is True
    assert resumed["count"] == 12

    before = resumed["latest"]
    ticked = client.post("/api/tick").json()
    assert ticked["count"] == 13
    assert ticked["latest"] > before

    cleared = client.post("/api/reset").json()
    assert cleared["count"] == 0
    assert cleared["status"] == "idle"


def test_tick_while_idle_does_not_invent_sales(client):
    body = client.post("/api/tick").json()
    assert body["count"] == 0
    assert body["status"] == "idle"
