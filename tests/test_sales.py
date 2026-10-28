from app.sales import SalesLedger


def test_start_seeds_a_climbing_total():
    ledger = SalesLedger(seed=7)
    snapshot = ledger.start()
    totals = [point["y"] for point in snapshot["points"]]
    assert snapshot["running"] is True
    assert snapshot["count"] == 12
    assert snapshot["status"] == "recording"
    assert snapshot["points"][0]["t"] == 1
    assert totals == sorted(totals)
    assert all(later > earlier for earlier, later in zip(totals, totals[1:]))
    assert snapshot["latest"] == totals[-1]
    assert snapshot["today"] == snapshot["points"][-1]["day_sales"]


def test_total_matches_the_sum_of_each_day():
    ledger = SalesLedger(seed=3)
    snapshot = ledger.start()
    for _ in range(20):
        snapshot = ledger.tick()
    expected = 0.0
    for point in snapshot["points"]:
        expected = round(expected + point["day_sales"], 2)
    assert snapshot["latest"] == expected
    assert snapshot["days"] == snapshot["count"]


def test_window_keeps_the_running_total():
    ledger = SalesLedger(seed=2)
    ledger.start()
    snapshot = ledger.snapshot()
    for _ in range(200):
        snapshot = ledger.tick()
    assert snapshot["count"] == ledger.capacity
    assert snapshot["days"] == 212
    assert snapshot["points"][0]["t"] == 212 - ledger.capacity + 1
    totals = [point["y"] for point in snapshot["points"]]
    assert all(later > earlier for earlier, later in zip(totals, totals[1:]))


def test_pause_keeps_the_total_and_resume_continues():
    ledger = SalesLedger(seed=1)
    ledger.start()
    paused = ledger.pause()
    assert paused["running"] is False
    assert paused["status"] == "paused"
    assert paused["count"] == 12
    held = paused["latest"]
    same = ledger.tick()
    assert same["count"] == 12
    assert same["latest"] == held
    resumed = ledger.resume()
    assert resumed["running"] is True
    assert resumed["count"] == 12
    nxt = ledger.tick()
    assert nxt["count"] == 13
    assert nxt["latest"] > held


def test_reset_returns_to_idle():
    ledger = SalesLedger(seed=1)
    ledger.start()
    cleared = ledger.reset()
    assert cleared["count"] == 0
    assert cleared["status"] == "idle"
    assert cleared["latest"] is None
    assert cleared["today"] is None
    assert cleared["running"] is False
