"""Draw the probe trace as an SVG figure."""

from __future__ import annotations

import re
import threading
from io import StringIO
from typing import Any

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"

from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

_lock = threading.Lock()


def render_svg(snapshot: dict[str, Any]) -> str:
    """Return a responsive SVG of temperature against elapsed seconds."""
    with _lock:
        fig = Figure(figsize=(9.4, 4.5), dpi=120)
        FigureCanvasSVG(fig)
        ax = fig.add_subplot(111)

        low, high = snapshot["band"]
        points = snapshot["points"]
        unit = snapshot["unit"]
        reading_color = matplotlib.rcParams["axes.prop_cycle"].by_key()["color"][0]

        band = ax.axhspan(low, high, alpha=0.15, zorder=0, linewidth=0)
        setpoint = ax.axhline(
            snapshot["setpoint"],
            linestyle="--",
            zorder=1,
        )

        line = None
        if points:
            times = [point["t"] for point in points]
            values = [point["y"] for point in points]
            (line,) = ax.plot(times, values, zorder=2)
            ax.scatter(
                [times[-1]],
                [values[-1]],
                s=32,
                color=line.get_color(),
                zorder=3,
                linewidths=0,
            )
            span = max(times[-1] - times[0], 1)
            pad = max(1.0, span * 0.02)
            ax.set_xlim(times[0] - pad * 0.15, times[-1] + pad)
            stacked = values + [low, high]
            y_pad = 0.55
            ax.set_ylim(min(stacked) - y_pad, max(stacked) + y_pad)
        else:
            ax.set_xlim(0, 60)
            ax.set_ylim(low - 1.4, high + 1.4)
            ax.text(
                0.5,
                0.58,
                "No samples yet",
                transform=ax.transAxes,
                ha="center",
                va="center",
            )

        ax.set_xlabel("Seconds on the probe clock")
        ax.set_ylabel(f"Temperature ({unit})")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(True, axis="y", zorder=0)
        reading = line or Line2D([0], [0], color=reading_color, label="Reading")
        ax.legend(
            handles=[
                reading,
                setpoint,
                Patch(
                    facecolor=band.get_facecolor(),
                    edgecolor="none",
                    label="Acceptable band",
                ),
            ],
            labels=[
                "Reading",
                f"Setpoint {snapshot['setpoint']:g}{unit}",
                "Acceptable band",
            ],
            frameon=False,
            loc="upper left",
        )
        fig.tight_layout(pad=0.7)

        buffer = StringIO()
        fig.savefig(buffer, format="svg")
        svg = buffer.getvalue()

    return _responsive(svg)


def _responsive(svg: str) -> str:
    """Let the page scale the figure without clipping the viewBox."""

    def fix(match: re.Match[str]) -> str:
        tag = match.group(0)
        tag = re.sub(r'\swidth="[^"]*"', ' width="100%"', tag, count=1)
        tag = re.sub(r'\sheight="[^"]*"', ' height="100%"', tag, count=1)
        return tag

    return re.sub(r"<svg\b[^>]*>", fix, svg, count=1)
