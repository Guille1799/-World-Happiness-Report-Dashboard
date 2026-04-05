# Screenshots

| File | Description |
|------|----------------|
| `dashboard-overview.png` | Cross-section grid (scatter, map, distribution, ranking) — used in the root README. |
| `demo.gif` | Short loop (Ken Burns zoom) generated from `dashboard-overview.png` — animated preview in the root README. |

Replace or add PNGs here (keep files small, < ~1 MB) and reference them from `README.md`.

**Regenerate `demo.gif`** (from repo root, requires [Pillow](https://pillow.readthedocs.io/)):

```bash
python -m pip install pillow
python scripts/make_demo_gif.py
```

**Clean map panel:** install all runtime dependencies so `streamlit-plotly-events` is available (see `world-happiness-streamlit/requirements.txt`). Otherwise the UI may show a one-line install hint above the map — hide that in captures by using a full `pip install -r requirements.txt` environment, or crop the image.
