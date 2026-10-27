from app.plot import render_svg
from app.sensor import SensorTrace


def _snapshot(seed: int, running: bool):
    trace = SensorTrace(seed=seed)
    if running:
        return trace.start()
    return trace.snapshot()


def test_empty_chart_is_a_responsive_svg():
    svg = render_svg(_snapshot(1, running=False))
    assert svg.lstrip().startswith("<?xml")
    assert '<svg' in svg
    assert 'width="100%"' in svg
    assert 'height="100%"' in svg
    assert "viewBox=" in svg


def test_live_chart_draws_a_trace():
    empty = render_svg(_snapshot(1, running=False))
    live = render_svg(_snapshot(4, running=True))
    assert live.count("<path") > empty.count("<path")
    assert "viewBox=" in live
