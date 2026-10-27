from app.sensor import SensorTrace


def test_start_seeds_a_short_trace():
    trace = SensorTrace(seed=7)
    snapshot = trace.start()
    assert snapshot["running"] is True
    assert snapshot["count"] == 12
    assert snapshot["status"] in {"steady", "low", "high"}
    assert snapshot["points"][0]["t"] == 1
    assert snapshot["points"][-1]["t"] == 12


def test_trace_scrolls_inside_a_fixed_window():
    trace = SensorTrace(seed=3)
    trace.start()
    for _ in range(200):
        snapshot = trace.tick()
    assert snapshot["count"] == trace.capacity
    assert snapshot["elapsed_s"] == 212
    assert snapshot["points"][0]["t"] == 212 - trace.capacity + 1
    assert all(-1.0 <= point["y"] <= 11.0 for point in snapshot["points"])


def test_pause_keeps_samples_and_resume_continues():
    trace = SensorTrace(seed=1)
    trace.start()
    paused = trace.pause()
    assert paused["running"] is False
    assert paused["status"] == "paused"
    assert paused["count"] == 12
    same = trace.tick()
    assert same["count"] == 12
    resumed = trace.resume()
    assert resumed["running"] is True
    assert resumed["count"] == 12
    nxt = trace.tick()
    assert nxt["count"] == 13
    assert nxt["elapsed_s"] == 13


def test_reset_returns_to_idle():
    trace = SensorTrace(seed=1)
    trace.start()
    cleared = trace.reset()
    assert cleared["count"] == 0
    assert cleared["status"] == "idle"
    assert cleared["latest"] is None
    assert cleared["running"] is False
