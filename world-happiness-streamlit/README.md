# World Happiness Intelligence (Streamlit)

This folder is the **Streamlit application**. For the full repository overview, badges, and roadmap, see the [**root README**](../README.md).

## Run locally

```bash
cd world-happiness-streamlit
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

**Tests:**

```bash
pip install -r requirements-dev.txt
pytest tests/ -q
```

## Data resolution (automatic)

1. **`WHR_DATA_PATH`** or Streamlit secret **`data_path`** — absolute path to a workbook (legacy or Figure 2.1); sheet layout is auto-detected.
2. **Legacy workbook** — `_WHR-Happiness - Dataset - v5.xlsx` in `data/` or next to `app.py`.
3. **Official WHR Figure 2.1** — `data/WHR26_Data_Figure_2.1.xlsx`; if missing, the app may download it (needs network). Set **`WHR_NO_AUTO_DOWNLOAD=1`** to disable.
4. **Demo** — `data/demo_whr.csv` (generate via `python scripts/generate_demo_whr.py`).

**Figure 2.1 mode:** axes labelled *Explained by: …* are **contributions to the national score**, not raw survey items. **Population** for bubble size is merged from a [public population dataset](https://github.com/datasets/population) when online; use `WHR_POPULATION_CSV` offline (see root `.env.example`).

## Deploy (Streamlit Community Cloud)

Repository root on GitHub → **Main file path:** `world-happiness-streamlit/app.py`, branch **`main`**.

**Docker:** see `Dockerfile` in this directory.

## Licence & attribution

Respect **World Happiness Report** and **Gallup** terms. This UI is exploratory and not affiliated with the WHR authors.
