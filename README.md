# Total sales

A small web app that plots a store's running sales total on an XY chart. Days run along the horizontal axis and the cumulative takings run along the vertical axis. The figure is drawn with [Matplotlib](https://github.com/tjws052009/matplotlib_test), installed from that repository.

Each point adds one simulated day from the front counter. The line starts at the first day's sales and only climbs.

## Run

The first install compiles Matplotlib, so you need Python 3.12 or newer, a C++ compiler, and the FreeType and libpng headers.

```bash
uv sync --extra dev
uv run sales-chart
```

Then open [http://127.0.0.1:8742](http://127.0.0.1:8742).

Start recording to draw the total. Pause keeps the line on the chart. Clear drops it.

## Tests

```bash
uv run pytest
```
