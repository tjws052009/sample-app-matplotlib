"""A mean-reverting temperature probe with a short memory."""

from __future__ import annotations

import random
import threading
from typing import Any

LIBRARY_SOURCE = "https://github.com/tjws052009/matplotlib_test"


class SensorTrace:
    """Simulated glycol-bath probe.

    Readings wander around a setpoint and are clipped to a physical range.
    The buffer keeps the last few minutes so the chart is a scrolling window.
    """

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._lock = threading.Lock()
        self.name = "Glycol bath"
        self.channel = "Probe A"
        self.room = "Cold room 2"
        self.unit = "°C"
        self.setpoint = 4.0
        self.low = 2.5
        self.high = 5.5
        self.capacity = 180
        self._y = self.setpoint
        self._t = 0
        self.points: list[tuple[int, float]] = []
        self.running = False

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return self._snapshot_locked()

    def start(self) -> dict[str, Any]:
        """Clear the trace and draw a short run so the chart is not a single dot."""
        with self._lock:
            self._y = self.setpoint + self._rng.uniform(-0.12, 0.12)
            self._t = 0
            self.points = []
            self.running = True
            for _ in range(12):
                self._step_locked()
            return self._snapshot_locked()

    def tick(self) -> dict[str, Any]:
        with self._lock:
            if self.running:
                self._step_locked()
            return self._snapshot_locked()

    def pause(self) -> dict[str, Any]:
        with self._lock:
            self.running = False
            return self._snapshot_locked()

    def resume(self) -> dict[str, Any]:
        """Continue the current trace. A cleared probe starts a new one."""
        with self._lock:
            if not self.points:
                self.running = True
                self._y = self.setpoint + self._rng.uniform(-0.12, 0.12)
                for _ in range(12):
                    self._step_locked()
            else:
                self.running = True
            return self._snapshot_locked()

    def reset(self) -> dict[str, Any]:
        with self._lock:
            self.running = False
            self._y = self.setpoint
            self._t = 0
            self.points = []
            return self._snapshot_locked()

    def _step_locked(self) -> None:
        pull = 0.08
        noise = self._rng.gauss(0, 0.05)
        self._y += pull * (self.setpoint - self._y) + noise
        if self._rng.random() < 0.025:
            self._y += self._rng.choice((-1.0, 1.0)) * self._rng.uniform(0.18, 0.42)
        self._y = min(11.0, max(-1.0, self._y))
        self._t += 1
        self.points.append((self._t, round(self._y, 3)))
        if len(self.points) > self.capacity:
            self.points = self.points[-self.capacity :]

    def _snapshot_locked(self) -> dict[str, Any]:
        ys = [y for _, y in self.points]
        latest = ys[-1] if ys else None
        if not ys:
            status = "idle"
        elif not self.running:
            status = "paused"
        elif latest < self.low:
            status = "low"
        elif latest > self.high:
            status = "high"
        else:
            status = "steady"
        mean = round(sum(ys) / len(ys), 3) if ys else None
        return {
            "room": self.room,
            "name": self.name,
            "channel": self.channel,
            "unit": self.unit,
            "setpoint": self.setpoint,
            "band": [self.low, self.high],
            "running": self.running,
            "status": status,
            "latest": latest,
            "minimum": min(ys) if ys else None,
            "maximum": max(ys) if ys else None,
            "mean": mean,
            "elapsed_s": self.points[-1][0] if self.points else 0,
            "count": len(self.points),
            "points": [{"t": t, "y": y} for t, y in self.points],
            "library": {
                "name": "matplotlib",
                "source": LIBRARY_SOURCE,
            },
        }
