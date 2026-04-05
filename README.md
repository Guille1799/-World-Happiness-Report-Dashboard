# World Happiness Report — Interactive Dashboard

[![CI](https://github.com/Guille1799/-World-Happiness-Report-Dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/Guille1799/-World-Happiness-Report-Dashboard/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

Exploratory analytics UI for **national life evaluations** (Cantril ladder, 0–10) and WHR-style drivers: **Plotly** maps, scatter plots, distributions, multi-country **trends**, CSV export, and **EN/ES** UI strings.  
**Live app:** [world-happiness-report-dash.streamlit.app](https://world-happiness-report-dash.streamlit.app/)

### Screenshots

The UI includes a cross-section **scatter** and **map**, **histograms**, **rankings**, and multi-country **trends** with CSV export.  
Open the **[live app](https://world-happiness-report-dash.streamlit.app/)** for the full experience.  
To add a static preview to this README later, drop a PNG under [`docs/images/`](docs/images/) and link it here.

This repository is a **monorepo**:

| Path | Purpose |
|------|---------|
| [`world-happiness-streamlit/`](world-happiness-streamlit/) | Main **Streamlit** application (`app.py`), tests, Docker, pinned `requirements.txt`. |
| [`shiny-dashboard-redirect/`](shiny-dashboard-redirect/) | Minimal **R/Shiny** app that **redirects** a legacy [shinyapps.io](https://www.shinyapps.io/) URL to the Streamlit deployment. |

---

## Features (Streamlit app)

- **Cross-section:** scatter (driver vs life evaluation), world choropleth, histogram, top/bottom bars, KPIs, automated insight bullets, optional **confidence intervals** when the WHR workbook provides whiskers.
- **Trends:** up to eight countries, year-window zoom, presets (regional groups + data-driven rankings), summary table with coverage / missing-year stats, shareable **query parameters** (`year`, `t0`, `t1`, `c`).
- **UX:** info popovers, safe linear fits when `numpy` SVD fails, graceful **offline** handling for optional World Bank population CSV.
- **i18n:** English and Spanish for major labels and help text.

---

## Tech stack

- Python **3.11+**, **Streamlit**, **Plotly**, **pandas**, **numpy**  
- Optional: **country_converter**, **streamlit-plotly-events** (map click-to-add)  
- Tests: **pytest** (`world-happiness-streamlit/tests/`)

---

## Quick start (local)

```bash
cd world-happiness-streamlit
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

**Developer install (includes pytest):**

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -q
```

Copy [`.env.example`](.env.example) to `.env` only on your machine if you need paths or flags — **never commit `.env`**.

---

## Deploy — Streamlit Community Cloud

1. Push this repo to GitHub.
2. Open [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. **New app** → select the repo, branch **`main`**, main file **`world-happiness-streamlit/app.py`**.
4. Add **Secrets** only if you use private data paths (same keys as `.env.example`).

---

## Legacy Shiny URL → Streamlit

If you still serve an old link on **shinyapps.io**, deploy the tiny app in [`shiny-dashboard-redirect/`](shiny-dashboard-redirect/) so it redirects to your Streamlit URL.  
Step-by-step: [`shiny-dashboard-redirect/DEPLOY-SHINY.md`](shiny-dashboard-redirect/DEPLOY-SHINY.md).

---

## Repository layout

```
world-happiness-streamlit/
  app.py              # Entry point
  i18n.py             # EN/ES strings
  insights.py         # Automated bullets + safe_pearson_r
  trend_helpers.py    # Presets, rankings, summary table
  tests/              # pytest
  data/demo_whr.csv   # Small demo dataset (committed)
shiny-dashboard-redirect/
  app.R               # Redirect target URL (Streamlit production)
scripts/
  push-to-github.ps1  # Optional: git remote + push (Windows)
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Security

Do not commit secrets. Report sensitive issues responsibly — see [SECURITY.md](SECURITY.md).

---

## License & data attribution

- **Code:** [MIT License](LICENSE).
- **Data:** [World Happiness Report](https://worldhappiness.report/) and **Gallup World Poll** data are subject to their terms. This project is **not** affiliated with the WHR, SDSN, or Gallup. World Bank–style population merge uses public registry data when online; a local CSV can be used offline.

---

## Roadmap (ideas to level up the project)

High impact, roughly ordered:

| Priority | Idea |
|----------|------|
| ★ | **CI** — GitHub Actions: **Ruff**, pytest, `py_compile` (see `.github/workflows/ci.yml`). |
| ★ | **Lint** — `ruff` + `pyproject.toml` in `world-happiness-streamlit/`. |
| | **Docs** — Drop a PNG into `docs/images/` and embed in README. |
| | **Coverage** — `pytest-cov` threshold on `trend_helpers` / `insights`. |
| | **pre-commit** — optional hooks calling `ruff check --fix`. |
| | **Accessibility** — keyboard focus, ARIA labels on custom HTML fragments. |
| | **Performance** — cache tuning, lazy imports for cold start on Streamlit Cloud. |
| | **Theming** — Streamlit theme file (dark/light) in `.streamlit/config.toml`. |
| | **API** — thin FastAPI export of summary stats (optional separate service). |

Contributions welcome — open an issue or PR.
