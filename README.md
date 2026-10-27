# Sensor trace

A small web app that plots a simulated cold-room probe on an XY chart. Time runs along the horizontal axis and temperature along the vertical axis. The figure is drawn with [Matplotlib](https://github.com/tjws052009/matplotlib_test), installed from that repository.

The probe is a glycol bath held near 4°C. Readings wander around the setpoint with a little noise, and the chart keeps the last three minutes.

## Run

The first install compiles Matplotlib, so you need Python 3.12 or newer, a C++ compiler, and the FreeType and libpng headers.

```bash
uv sync --extra dev
uv run sensor-trace
```

Then open [http://127.0.0.1:8742](http://127.0.0.1:8742).

Start logging to draw the trace. Pause keeps the samples on the chart. Clear drops them.

## Tests

```bash
uv run pytest
```
