"""Web app that serves the probe chart."""

from __future__ import annotations

from pathlib import Path

import matplotlib
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response

from app.plot import render_svg
from app.sensor import LIBRARY_SOURCE, SensorTrace

app = FastAPI(title="Glycol bath probe", docs_url=None, redoc_url=None)
trace = SensorTrace()
_page = (Path(__file__).parent / "templates" / "index.html").read_text(encoding="utf-8")


def _payload(snapshot: dict) -> dict:
    snapshot["library"]["version"] = matplotlib.__version__
    snapshot["library"]["source"] = LIBRARY_SOURCE
    return snapshot


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return _page


@app.get("/api/trace")
def read_trace() -> dict:
    return _payload(trace.snapshot())


@app.post("/api/start")
def start() -> dict:
    return _payload(trace.start())


@app.post("/api/tick")
def tick() -> dict:
    return _payload(trace.tick())


@app.post("/api/pause")
def pause() -> dict:
    return _payload(trace.pause())


@app.post("/api/resume")
def resume() -> dict:
    return _payload(trace.resume())


@app.post("/api/reset")
def reset() -> dict:
    return _payload(trace.reset())


@app.get("/plot.svg")
def plot() -> Response:
    svg = render_svg(trace.snapshot())
    return Response(
        content=svg,
        media_type="image/svg+xml",
        headers={"Cache-Control": "no-store"},
    )


def main() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8742, reload=False)
