# Drawings

| Sheet | File | Shows |
|---|---|---|
| E-01 | [E-01-control-interconnection.svg](E-01-control-interconnection.svg) | Control-system block wiring. The panel (CP-1), controller and three Modbus modules, power and fusing, and the RS485 bus. Every relay output, digital input and analogue input is wired to its field device. |
| P-01 | [P-01-piping-instrumentation.svg](P-01-piping-instrumentation.svg) | Indicative piping and instrumentation. Where the temperature elements (TE), level transmitters (LT), flow switches (FS), JVAs and top-up valves sit in the indoor and outdoor/spa circuits. |

Both sheets are **Revision A — draft, not for construction**. Tags and relay channels match [PLAN.md](../PLAN.md) §6. Pipe routes and JVA functions on P-01 are to be confirmed at the site survey (PLAN §14).

## Regenerating

The SVGs are generated from the Python scripts in `src/`. Edit the script, not the SVG.

```
cd docs/drawings/src
python e01.py ../E-01-control-interconnection.svg
python p01.py ../P-01-piping-instrumentation.svg
```

`render.py` makes a PNG preview with Playwright (optional):

```
python render.py <svg> <png> <width> <height>
```
