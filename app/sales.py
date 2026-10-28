"""A store ledger whose total only climbs."""

from __future__ import annotations

import random
import threading
from typing import Any

LIBRARY_SOURCE = "https://github.com/tjws052009/matplotlib_test"


class SalesLedger:
    """Simulated front-counter takings.

    Each step is one day. The plotted value is the running total, so the
    line starts at the first day's sales and never turns down.
    """

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._lock = threading.Lock()
        self.store = "Store 4"
        self.name = "Total sales"
        self.counter = "Front counter"
        self.unit = "USD"
        self.capacity = 180
        self._day = 0
        self._total = 0.0
        self.points: list[tuple[int, float, float]] = []
        self.running = False

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return self._snapshot_locked()

    def start(self) -> dict[str, Any]:
        """Clear the ledger and record a short opening run."""
        with self._lock:
            self._day = 0
            self._total = 0.0
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
        """Continue the current total. An empty ledger starts a new one."""
        with self._lock:
            if not self.points:
                self.running = True
                self._day = 0
                self._total = 0.0
                for _ in range(12):
                    self._step_locked()
            else:
                self.running = True
            return self._snapshot_locked()

    def reset(self) -> dict[str, Any]:
        with self._lock:
            self.running = False
            self._day = 0
            self._total = 0.0
            self.points = []
            return self._snapshot_locked()

    def _day_sales(self) -> float:
        weekend = self._day % 7 in (6, 0)
        base = 2460.0 if weekend else 1680.0
        amount = base + self._rng.gauss(0, 210)
        if self._rng.random() < 0.08:
            amount += self._rng.uniform(700, 1900)
        return round(max(180.0, amount), 2)

    def _step_locked(self) -> None:
        self._day += 1
        sold = self._day_sales()
        self._total = round(self._total + sold, 2)
        self.points.append((self._day, self._total, sold))
        if len(self.points) > self.capacity:
            self.points = self.points[-self.capacity :]

    def _snapshot_locked(self) -> dict[str, Any]:
        if not self.points:
            status = "idle"
            latest = None
            today = None
            average = None
        else:
            status = "recording" if self.running else "paused"
            latest = self.points[-1][1]
            today = self.points[-1][2]
            average = round(sum(point[2] for point in self.points) / len(self.points), 2)
        return {
            "store": self.store,
            "name": self.name,
            "counter": self.counter,
            "unit": self.unit,
            "running": self.running,
            "status": status,
            "latest": latest,
            "today": today,
            "average": average,
            "days": self.points[-1][0] if self.points else 0,
            "count": len(self.points),
            "points": [
                {"t": day, "y": total, "day_sales": sold}
                for day, total, sold in self.points
            ],
            "library": {
                "name": "matplotlib",
                "source": LIBRARY_SOURCE,
            },
        }
