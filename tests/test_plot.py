from app.plot import render_svg
from app.sales import SalesLedger


def _snapshot(seed: int, running: bool):
    ledger = SalesLedger(seed=seed)
    if running:
        return ledger.start()
    return ledger.snapshot()


def test_empty_chart_is_a_responsive_svg():
    svg = render_svg(_snapshot(1, running=False))
    assert svg.lstrip().startswith("<?xml")
    assert "<svg" in svg
    assert 'width="100%"' in svg
    assert 'height="100%"' in svg
    assert "viewBox=" in svg


def test_live_chart_draws_a_climbing_total():
    empty = render_svg(_snapshot(1, running=False))
    live = render_svg(_snapshot(4, running=True))
    assert live.count("<path") > empty.count("<path")
    assert "viewBox=" in live
