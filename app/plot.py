"""Draw cumulative sales as an SVG line."""

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
from matplotlib.ticker import FuncFormatter

_lock = threading.Lock()


def _dollars(value: float, _position: int) -> str:
    return f"${value:,.0f}"


def render_svg(snapshot: dict[str, Any]) -> str:
    """Return a responsive SVG of total sales against day number."""
    with _lock:
        fig = Figure(figsize=(9.4, 4.5), dpi=120)
        FigureCanvasSVG(fig)
        ax = fig.add_subplot(111)

        points = snapshot["points"]
        if points:
            days = [point["t"] for point in points]
            totals = [point["y"] for point in points]
            (line,) = ax.plot(days, totals, zorder=2)
            ax.scatter(
                [days[-1]],
                [totals[-1]],
                s=32,
                color=line.get_color(),
                zorder=3,
                linewidths=0,
            )
            span = max(days[-1] - days[0], 1)
            pad = max(0.4, span * 0.02)
            ax.set_xlim(days[0] - pad * 0.15, days[-1] + pad)
            top = max(totals) * 1.08
            if days[0] == 1:
                ax.set_ylim(0, top)
            else:
                floor = min(totals) * 0.97
                ax.set_ylim(floor, max(top, floor + 1))
            ax.legend(
                [line],
                ["Total sales"],
                frameon=False,
                loc="upper left",
            )
        else:
            ax.set_xlim(0, 30)
            ax.set_ylim(0, 5000)
            ax.text(
                0.5,
                0.58,
                "No sales yet",
                transform=ax.transAxes,
                ha="center",
                va="center",
            )

        ax.set_xlabel("Day")
        ax.set_ylabel("Total sales ($)")
        ax.yaxis.set_major_formatter(FuncFormatter(_dollars))
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(True, axis="y", zorder=0)
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
