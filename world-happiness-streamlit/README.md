# World Happiness Intelligence

Interactive **Streamlit** dashboard for exploring national **life evaluations** (Cantril ladder, 0–10) together with economic and social drivers. Built with **Plotly** for maps, scatter plots, distributions, and time series.

**Features:** regional **presets** (incl. Benelux, Baltic, English-speaking, etc.), **data-driven** shortcuts (largest gain/decline over the sample, volatility, range, vs-global change, linear slopes), snapshot **top/bottom** for the selected year, search-and-**add**, CSV **export** of the cross-section, **trend** chart with optional **year-window** zoom, **summary table** + CSV downloads for country/global series, unified crosshair (`hovermode`), and an expander documenting **preset definitions**.

## Is it online?

The app is **local** until you deploy it. Typical free hosting: push this folder to **GitHub** and connect the repo to **[Streamlit Community Cloud](https://share.streamlit.io)** to get a public URL (`https://<your-app>.streamlit.app`).

## Data sources (automatic resolution)

1. **`WHR_DATA_PATH`** or Streamlit secret **`data_path`** — absolute path to your workbook (legacy or Figure 2.1 format; the app detects sheet layout).
2. **Legacy workbook** — `_WHR-Happiness - Dataset - v5.xlsx` in `data/` or next to `app.py` (course / Gapminder-style sheets).
3. **Official WHR 2026 Figure 2.1** — `data/WHR26_Data_Figure_2.1.xlsx`. If missing, the app can **download** it from `files.worldhappiness.report` (requires internet). Set **`WHR_NO_AUTO_DOWNLOAD=1`** to disable automatic download.
4. **Demo** — `data/demo_whr.csv` (generate with `python scripts/generate_demo_whr.py`).

**Figure 2.1 mode:** horizontal axes labelled *Explained by: …* are **contributions to the national score**, not raw panel indicators. **Population** for bubble size is merged from the [World Bank–based population dataset](https://github.com/datasets/population) (ISO-3166 alpha-3, as-of merge by year).

## Run locally

```bash
cd world-happiness-streamlit
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy (GitHub + Streamlit Cloud)

1. Create a GitHub repository and push this directory.
2. Sign in at [share.streamlit.io](https://share.streamlit.io) with GitHub.
3. **New app** → select the repo, branch `main`, main file **`app.py`**.
4. Add **Secrets** if your data file is not in the repo (or commit a small dataset / allow the app to download Figure 2.1 on first run).
5. Your app URL will look like `https://<name>.streamlit.app`.

**Note:** GitHub Pages does not run Python backends; use Streamlit Cloud, Render, Railway, or Docker with  
`streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`.

## Licence & attribution

Respect the **World Happiness Report** and underlying **Gallup World Poll** terms. When using Gapminder or World Bank–derived series, retain their attribution requirements. This repository is an exploratory UI only; it is not affiliated with the WHR authors.
