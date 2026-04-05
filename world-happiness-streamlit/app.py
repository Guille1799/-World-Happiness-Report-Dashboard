"""
World Happiness Intelligence — Streamlit (Python).
Deploy: push to GitHub → https://streamlit.io/cloud (free) → public URL.
"""

from __future__ import annotations

import os
import urllib.request
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from i18n import tr
from insights import compute_insights, safe_pearson_r
from trend_helpers import (
    MAX_TREND_COUNTRIES,
    apply_preset,
    sparse_country_warning,
    trend_biggest_gains,
    trend_biggest_losses,
    trend_by_slope,
    trend_largest_range,
    trend_most_volatile,
    trend_summary_table,
    trend_vs_global_delta_spread,
)

try:
    import country_converter as coco
except ImportError:
    coco = None

try:
    from streamlit_plotly_events import plotly_events

    HAS_PLOTLY_EVENTS = True
except ImportError:
    plotly_events = None
    HAS_PLOTLY_EVENTS = False


def _qp_get_int(qp: object, key: str, lo: int, hi: int, default: int) -> int:
    try:
        v = qp.get(key)  # type: ignore[union-attr]
    except Exception:
        return default
    if v is None:
        return default
    if isinstance(v, list):
        v = v[0]
    try:
        n = int(str(v))
        if lo <= n <= hi:
            return n
    except ValueError:
        pass
    return default


WH_SOURCE = "World Happiness Report & Gallup World Poll"
WH_SOURCE_FIGURE21 = (
    "World Happiness Report — Figure 2.1 (three-year rolling averages) · "
    "Population: World Bank national totals (datasets registry)"
)
WH_SOURCE_DEMO = "Synthetic demo dataset (local CSV only)"

WHR_FIGURE21_URL = "https://files.worldhappiness.report/WHR26_Data_Figure_2.1.xlsx"
WHR_FIGURE21_FILENAME = "WHR26_Data_Figure_2.1.xlsx"
POP_WORLD_BANK_CSV = "https://raw.githubusercontent.com/datasets/population/master/data/population.csv"

X_LABELS = {
    "GDP": "Log GDP per capita",
    "SocialSupport": "Social support",
    "HealthyLifeExpectancy": "Healthy life expectancy at birth",
    "Freedom": "Freedom to make life choices",
    "Corruption": "Perceptions of corruption",
    "Generosity": "Generosity",
}

# WHR Figure 2.1 workbook: columns are *explained-by* contributions to the national score, not raw indicators.
FIGURE21_X_LABELS = {
    "GDP": "Explained by: log GDP per capita",
    "SocialSupport": "Explained by: social support",
    "HealthyLifeExpectancy": "Explained by: healthy life expectancy",
    "Freedom": "Explained by: freedom to make life choices",
    "Corruption": "Explained by: perceptions of corruption",
    "Generosity": "Explained by: generosity",
}

# Scatter vs map row: same height so the choropleth matches the scatter; plotly_events needs matching override_height.
_CROSS_ROW_PLOT_HEIGHT = 520


def _inject_app_styles() -> None:
    st.markdown(
        """
<style>
    .whr-main-title { font-weight: 700; letter-spacing: -0.03em; color: #0f172a; margin-bottom: 0.15rem; }
    .whr-sub { color: #64748b; font-size: 0.95rem; margin-top: 0; }
    div[data-testid="stSidebarHeader"] { padding-bottom: 0.5rem; }
    /* Sidebar expanders (e.g. Quick reference): keep them readable */
    section[data-testid="stSidebar"] details[data-testid="stExpander"] summary {
        font-size: 1.05rem;
        padding: 0.15rem 0;
    }
    section[data-testid="stSidebar"] details[data-testid="stExpander"] {
        border: 1px solid #e2e8f0;
        border-radius: 0.35rem;
        background: #f8fafc;
    }
</style>
        """,
        unsafe_allow_html=True,
    )


def _truthy_env_or_secret(val: object) -> bool:
    if val is True:
        return True
    if val is False or val is None:
        return False
    s = str(val).strip().lower()
    return s in ("1", "true", "yes", "on")


def _hide_demo_banner() -> bool:
    """Hide the yellow demo strip (env vars or Streamlit Cloud Secrets)."""
    keys = ("WHR_HIDE_DEMO_BANNER", "HIDE_DEMO_BANNER")
    for k in keys:
        v = os.environ.get(k)
        if v is not None and _truthy_env_or_secret(v):
            return True
    try:
        sec = st.secrets
        for k in keys:
            try:
                v = sec[k]
            except Exception:
                continue
            if _truthy_env_or_secret(v):
                return True
    except Exception:
        pass
    return False


def _render_demo_mode_banner() -> None:
    """Full-bleed banner at the very top of the page (above main column width)."""
    st.markdown(
        """
<style>
    .whr-demo-fw {
        width: 100vw;
        position: relative;
        left: 50%;
        right: 50%;
        margin-left: -50vw;
        margin-right: -50vw;
        box-sizing: border-box;
        background: #fff3cd;
        border-bottom: 1px solid #e6ca72;
        padding: 0.55rem 1rem 0.6rem;
        font-size: 0.9rem;
        text-align: center;
        color: #1f2937;
        margin-bottom: 0.85rem;
    }
    .whr-demo-fw code { font-size: 0.85em; }
</style>
<div class="whr-demo-fw">
<strong>Demo mode</strong> (<code>data/demo_whr.csv</code>). For production data, allow the app to download
<code>WHR26_Data_Figure_2.1.xlsx</code>, place your own Excel under <code>data/</code>, or unset
<code>WHR_NO_AUTO_DOWNLOAD</code> if you disabled automatic download.
</div>
        """,
        unsafe_allow_html=True,
    )


def _inline_tip(lang: str, key: str) -> None:
    """Popover overlay (ℹ️). st.expander grows in-page and pushes all widgets downward — bad UX."""
    body = tr(lang, key)
    with st.popover("ℹ️", use_container_width=False):
        st.markdown(body)


def _title_with_tip(lang: str, title_md: str, tip_key: str) -> None:
    """Section title (markdown) with info icon column."""
    left, right = st.columns([0.94, 0.06])
    with left:
        st.markdown(title_md)
    with right:
        _inline_tip(lang, tip_key)


def _sync_trend_selection(countries: list[str]) -> None:
    """Reset or prune country selection when the underlying country list changes."""
    avail = set(countries)
    sig = hash(tuple(sorted(countries)))
    if st.session_state.get("_trend_country_sig") != sig:
        st.session_state["_trend_country_sig"] = sig
        from_url: list[str] = []
        try:
            cp = st.query_params.get("c")  # type: ignore[union-attr]
            if cp is not None:
                if isinstance(cp, list):
                    cp = cp[0]
                from_url = [
                    x.strip()
                    for x in str(cp).split("|")
                    if x.strip() and x.strip() in avail
                ][:MAX_TREND_COUNTRIES]
        except Exception:
            pass
        if from_url:
            st.session_state.trend_countries = from_url
        else:
            seed = [c for c in ("Spain", "Germany", "France", "Finland") if c in avail][:4]
            if not seed:
                seed = sorted(avail)[: min(4, len(avail))]
            st.session_state.trend_countries = seed
    else:
        cur = [c for c in st.session_state.get("trend_countries", []) if c in avail]
        st.session_state.trend_countries = cur[:MAX_TREND_COUNTRIES]


def plotly_config_trend() -> dict:
    """Allow export in trend chart; keep main charts clean."""
    return {"displayModeBar": True, "displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]}


def _detect_xlsx_kind(path: Path) -> Literal["legacy", "figure21"]:
    xl = pd.ExcelFile(path)
    if "input-data2008-2023_Happiness_I" in xl.sheet_names:
        return "legacy"
    return "figure21"


def _resolve_explicit_path() -> tuple[Path, Literal["legacy", "figure21"]] | None:
    candidates: list[str] = []
    try:
        p = st.secrets.get("data_path")
        if p:
            candidates.append(str(p))
    except Exception:
        pass
    env = os.environ.get("WHR_DATA_PATH")
    if env:
        candidates.append(env)
    for c in candidates:
        q = Path(c)
        if q.is_file():
            return q, _detect_xlsx_kind(q)
    return None


def _local_legacy_path() -> Path | None:
    here = Path(__file__).resolve().parent
    for name in (
        "data/_WHR-Happiness - Dataset - v5.xlsx",
        "_WHR-Happiness - Dataset - v5.xlsx",
    ):
        cand = here / name
        if cand.is_file():
            return cand
    return None


def _figure21_local_path() -> Path:
    return Path(__file__).resolve().parent / "data" / WHR_FIGURE21_FILENAME


def _ensure_figure21_xlsx() -> Path | None:
    """Use local copy in data/, or download from files.worldhappiness.report once."""
    p = _figure21_local_path()
    if p.is_file():
        return p
    if os.environ.get("WHR_NO_AUTO_DOWNLOAD"):
        return None
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(WHR_FIGURE21_URL, p)
        return p
    except Exception:
        return None


def _demo_csv_path() -> Path | None:
    here = Path(__file__).resolve().parent
    p = here / "data" / "demo_whr.csv"
    return p if p.is_file() else None


@st.cache_data(show_spinner="Loading data…")
def load_whr_data(path: str) -> pd.DataFrame:
    sheet_h = "input-data2008-2023_Happiness_I"
    sheet_p = "datapop#v8@fasttrackyearcountri"

    h = pd.read_excel(path, sheet_name=sheet_h)
    h = h.rename(
        columns={
            "Country name": "Country",
            "year": "Year",
            "Life Ladder": "Happiness",
            "Log GDP per capita": "GDP",
            "Social support": "SocialSupport",
            "Healthy life expectancy at birth": "HealthyLifeExpectancy",
            "Freedom to make life choices": "Freedom",
            "Perceptions of corruption": "Corruption",
            "Generosity": "Generosity",
        }
    )
    cols = [
        "Country",
        "Year",
        "Happiness",
        "GDP",
        "SocialSupport",
        "HealthyLifeExpectancy",
        "Freedom",
        "Corruption",
        "Generosity",
    ]
    h = h[cols].dropna()

    p = pd.read_excel(path, sheet_name=sheet_p)
    p = p.rename(columns={"name": "Country", "time": "Year", "Population": "Population"})
    p = p[["Country", "Year", "Population"]].dropna()

    df = h.merge(p, on=["Country", "Year"], how="inner")

    if coco is not None:
        cc = coco.CountryConverter()
        df["iso_a3"] = cc.convert(df["Country"].tolist(), to="ISO3")
    else:
        df["iso_a3"] = np.nan

    df = df.dropna(subset=["iso_a3"])
    s = df["iso_a3"].astype(str)
    df = df[s.str.len().eq(3) & ~s.str.lower().eq("not found")]
    return df


def _attach_population_by_year(h: pd.DataFrame, pop: pd.DataFrame) -> pd.DataFrame:
    """Merge-asof population (latest year ≤ WHR year) per ISO3."""

    def attach(g: pd.DataFrame) -> pd.DataFrame:
        iso = g.name
        sub = pop[pop["iso_a3"] == iso].sort_values("Year")
        g2 = g.sort_values("Year")
        if sub.empty:
            out = g2.copy()
            out["Population"] = np.nan
            return out
        return pd.merge_asof(g2, sub, on="Year", direction="backward")

    return h.groupby("iso_a3", group_keys=False).apply(attach)


def _empty_population_df() -> pd.DataFrame:
    return pd.DataFrame(columns=["iso_a3", "Year", "Population"])


def _normalize_population_df(pop: pd.DataFrame) -> pd.DataFrame:
    p = pop.copy()
    if "Country Code" in p.columns:
        p = p.rename(columns={"Country Code": "iso_a3"})
    if "Value" in p.columns and "Population" not in p.columns:
        p = p.rename(columns={"Value": "Population"})
    need = ["iso_a3", "Year", "Population"]
    missing = [c for c in need if c not in p.columns]
    if missing:
        raise ValueError(f"Population table missing columns {missing}; found {list(p.columns)}")
    out = p[need].dropna()
    out["Year"] = out["Year"].astype(int)
    return out


@st.cache_data(show_spinner="Loading population series…", ttl=86400)
def _load_worldbank_population_from_url() -> pd.DataFrame:
    pop = pd.read_csv(POP_WORLD_BANK_CSV)
    return _normalize_population_df(pop)


def _load_population_table() -> tuple[pd.DataFrame, Literal["local", "url", "empty"]]:
    """World Bank-style population (ISO3 × year). Local file or URL; empty if offline."""
    here = Path(__file__).resolve().parent
    candidates: list[Path] = []
    for key in ("WHR_POPULATION_CSV", "POPULATION_CSV_PATH"):
        env_p = os.environ.get(key)
        if env_p:
            candidates.append(Path(env_p).expanduser())
    candidates.extend(
        [
            here / "data" / "worldbank_population.csv",
            here / "data" / "population.csv",
        ]
    )
    for path in candidates:
        if path.is_file():
            try:
                pop = pd.read_csv(path)
                st.session_state.pop("_wb_pop_network_disabled", None)
                return _normalize_population_df(pop), "local"
            except Exception:
                continue
    if st.session_state.get("_wb_pop_network_disabled"):
        return _empty_population_df(), "empty"
    try:
        out = _load_worldbank_population_from_url()
        st.session_state.pop("_wb_pop_network_disabled", None)
        return out, "url"
    except Exception:
        st.session_state["_wb_pop_network_disabled"] = True
        return _empty_population_df(), "empty"


@st.cache_data(show_spinner="Loading WHR Fig. 2.1…")
def _parse_whr_figure21_excel(path: str) -> pd.DataFrame:
    raw = pd.read_excel(path, sheet_name=0)
    rename_map = {
        "Country name": "Country",
        "Life evaluation (3-year average)": "Happiness",
        "Explained by: Log GDP per capita": "GDP",
        "Explained by: Social support": "SocialSupport",
        "Explained by: Healthy life expectancy": "HealthyLifeExpectancy",
        "Explained by: Freedom to make life choices": "Freedom",
        "Explained by: Perceptions of corruption": "Corruption",
        "Explained by: Generosity": "Generosity",
    }
    if "Lower whisker" in raw.columns and "Upper whisker" in raw.columns:
        rename_map["Lower whisker"] = "Happiness_ci_low"
        rename_map["Upper whisker"] = "Happiness_ci_high"
    h = raw.rename(columns=rename_map)
    cols = [
        "Country",
        "Year",
        "Happiness",
        "GDP",
        "SocialSupport",
        "HealthyLifeExpectancy",
        "Freedom",
        "Corruption",
        "Generosity",
    ]
    if "Happiness_ci_low" in h.columns:
        cols += ["Happiness_ci_low", "Happiness_ci_high"]
    h = h[cols].dropna(subset=["Country", "Year", "Happiness"])
    h["Year"] = h["Year"].astype(int)

    if coco is None:
        raise RuntimeError("country_converter is required for official WHR data.")

    cc = coco.CountryConverter()
    h["iso_a3"] = cc.convert(h["Country"].tolist(), to="ISO3")
    s = h["iso_a3"].astype(str)
    h = h[s.str.len().eq(3) & ~s.str.lower().eq("not found")].copy()
    return h


def load_whr_figure21(path: str) -> pd.DataFrame:
    h = _parse_whr_figure21_excel(path)
    pop, src = _load_population_table()
    if src != "empty":
        st.session_state.pop("_pop_warned_shown", None)
    elif not st.session_state.get("_pop_warned_shown"):
        st.session_state["_show_pop_note"] = True
    h = _attach_population_by_year(h, pop)
    med = float(h["Population"].median()) if h["Population"].notna().any() else 1.0
    h["Population"] = h["Population"].fillna(med)
    return h


@st.cache_data(show_spinner="Loading demo data…")
def load_demo_data(path: str) -> pd.DataFrame:
    """Bundled CSV when the official WHR Excel is not available."""
    df = pd.read_csv(path)
    need = [
        "Country",
        "Year",
        "Happiness",
        "GDP",
        "SocialSupport",
        "HealthyLifeExpectancy",
        "Freedom",
        "Corruption",
        "Generosity",
        "Population",
        "iso_a3",
    ]
    missing = [c for c in need if c not in df.columns]
    if missing:
        raise ValueError(f"demo_whr.csv missing columns: {missing}")
    df = df[need].dropna()
    df["Year"] = df["Year"].astype(int)
    s = df["iso_a3"].astype(str)
    df = df[s.str.len().eq(3) & ~s.str.lower().eq("not found")]
    return df


def plotly_config():
    return {"displayModeBar": False, "displaylogo": False}


def _safe_polyfit_deg1(x: np.ndarray, y: np.ndarray) -> np.ndarray | None:
    """Linear least squares (degree 1). Returns ``[slope, intercept]`` (polyfit order) or ``None``."""
    xv = np.asarray(x, dtype=np.float64).ravel()
    yv = np.asarray(y, dtype=np.float64).ravel()
    mask = np.isfinite(xv) & np.isfinite(yv)
    xv = xv[mask]
    yv = yv[mask]
    if len(xv) < 2:
        return None
    xm = xv - float(np.mean(xv))
    denom = float(np.dot(xm, xm))
    if not np.isfinite(denom) or denom < 1e-20:
        return None
    try:
        return np.polyfit(xv, yv, 1)
    except np.linalg.LinAlgError:
        pass
    slope = float(np.dot(xm, yv - float(np.mean(yv))) / denom)
    intercept = float(np.mean(yv) - slope * np.mean(xv))
    return np.array([slope, intercept])


def main():
    st.set_page_config(
        page_title="World Happiness Intelligence",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.session_state.setdefault("lang", "en")

    demo_path = _demo_csv_path()
    explicit = _resolve_explicit_path()
    data_profile: Literal["legacy", "figure21", "demo"]

    if explicit is not None:
        exp_path, kind = explicit
        if kind == "legacy":
            df = load_whr_data(str(exp_path))
            x_labels = X_LABELS
            wh_source = WH_SOURCE
            data_profile = "legacy"
        else:
            df = load_whr_figure21(str(exp_path))
            x_labels = FIGURE21_X_LABELS
            wh_source = WH_SOURCE_FIGURE21
            data_profile = "figure21"
    elif (p_legacy := _local_legacy_path()) is not None:
        df = load_whr_data(str(p_legacy))
        x_labels = X_LABELS
        wh_source = WH_SOURCE
        data_profile = "legacy"
    elif (p_fig := _ensure_figure21_xlsx()) is not None:
        df = load_whr_figure21(str(p_fig))
        x_labels = FIGURE21_X_LABELS
        wh_source = WH_SOURCE_FIGURE21
        data_profile = "figure21"
    elif demo_path is not None:
        df = load_demo_data(str(demo_path))
        x_labels = X_LABELS
        wh_source = WH_SOURCE_DEMO
        data_profile = "demo"
    else:
        st.error(
            "No dataset available. Options: (1) Internet access so the app can fetch `WHR26_Data_Figure_2.1.xlsx` into "
            "`data/`, (2) download it manually from the "
            "[World Happiness Report data page](https://worldhappiness.report/data-sharing/), "
            "(3) add a legacy workbook (`_WHR-Happiness - Dataset - v5.xlsx`), or "
            "(4) run `python scripts/generate_demo_whr.py` to build `data/demo_whr.csv`."
        )
        st.stop()

    if data_profile == "demo" and not _hide_demo_banner():
        _render_demo_mode_banner()

    if st.session_state.pop("_show_pop_note", False):
        st.warning(
            "Could not load World Bank population data (offline, DNS error, or blocked URL). "
            "Scatter marker sizes use a neutral placeholder. To fix: download "
            "[population.csv](https://raw.githubusercontent.com/datasets/population/master/data/population.csv) "
            "and save it as `data/worldbank_population.csv`, or set env `WHR_POPULATION_CSV` to the file path, "
            "then refresh."
        )
        st.session_state["_pop_warned_shown"] = True

    year_min = int(df["Year"].min())
    year_max = int(df["Year"].max())
    happy_min = float(df["Happiness"].min())
    happy_max = float(df["Happiness"].max())
    countries = sorted(df["Country"].unique().tolist())

    if "ref_year" not in st.session_state:
        st.session_state.ref_year = _qp_get_int(st.query_params, "year", year_min, year_max, year_max)
    if "trend_year_window" not in st.session_state:
        _t0 = _qp_get_int(st.query_params, "t0", year_min, year_max, year_min)
        _t1 = _qp_get_int(st.query_params, "t1", year_min, year_max, year_max)
        st.session_state.trend_year_window = (min(_t0, _t1), max(_t0, _t1))

    subtitle = {
        "legacy": "Legacy panel workbook (course / Gapminder-style sheets)",
        "figure21": "Official WHR 2026 — Figure 2.1 (three-year rolling national averages)",
        "demo": "Synthetic demonstration dataset",
    }[data_profile]
    gdp_fit_label = (
        "log GDP per capita" if data_profile != "figure21" else "GDP contribution to the national score (explained-by)"
    )

    _inject_app_styles()
    st.title("World Happiness Intelligence")
    st.caption(subtitle)

    with st.expander("About & methodology", expanded=False):
        st.markdown(
            """
**Purpose.** Explore cross-country life evaluations (Cantril ladder, 0–10) alongside economic and social
indicators. This dashboard is for **exploratory analysis** and communication — not causal inference.

**What you see.**
- **Scatter:** association between the selected driver and national mean life evaluation for the chosen year.
  Marker area scales with **population** (World Bank totals merged by ISO-3166 alpha-3 where applicable).
- **Map:** same life-evaluation values on a world choropleth (ISO-3 codes).
- **Distribution & ranking:** histogram of life evaluations; top and bottom countries for the year.
- **Trends:** country trajectories against the **unweighted global mean** across years in the sample.

**Interpretation.** Correlations describe **co-movement**, not causal effects. Residuals in the executive snapshot
use a simple **linear fit on the GDP dimension** (raw log GDP in legacy mode; *explained-by* GDP contribution when
using the official Figure 2.1 workbook).

**Data source (this session).**
            """
        )
        st.markdown(f"_{wh_source}_")

    with st.sidebar:
        st.radio(
            "Language / Idioma",
            ["en", "es"],
            horizontal=True,
            key="lang",
        )
        lang = st.session_state.lang
        ac_l, ac_r = st.columns([0.82, 0.18])
        with ac_l:
            st.markdown(tr(lang, "analysis_controls"))
        with ac_r:
            _inline_tip(lang, "tip_sidebar_controls")
        st.caption(tr(lang, "sidebar_caption"))
        st.caption(tr(lang, "sidebar_data_span").format(year_min=year_min, year_max=year_max))
        year = st.slider(
            tr(lang, "ref_year"),
            year_min,
            year_max,
            key="ref_year",
            help=tr(lang, "help_ref_year"),
        )
        try:
            st.query_params["year"] = str(year)
        except Exception:
            pass
        rank_n = st.slider(tr(lang, "rank_n"), 5, 20, 10, help=tr(lang, "help_rank_n"))
        x_metric = st.selectbox(
            tr(lang, "scatter_axis"),
            options=list(x_labels.keys()),
            format_func=lambda k: x_labels[k],
            index=0,
            help=tr(lang, "help_scatter_axis"),
        )
        with st.expander(tr(lang, "quick_ref")):
            st.markdown(
                "- Scatter plots show **association**, not causation.\n"
                "- Residual highlight uses a simple linear benchmark on the **GDP dimension**.\n"
                f"- **Source:** {wh_source}"
            )

    df_y = df[df["Year"] == year].copy()
    n_ct = df_y["Country"].nunique()
    x_label = x_labels[x_metric]

    _title_with_tip(lang, tr(lang, "cross_section"), "tip_cross_section")
    st.caption(
        tr(lang, "caption_cross_section").format(
            year=year,
            n_ct=n_ct,
            year_min=year_min,
            year_max=year_max,
        )
    )

    # --- KPIs
    m1, m2, m3, m4 = st.columns(4)
    gavg = df_y["Happiness"].mean()
    top = df_y.nlargest(1, "Happiness").iloc[0]
    bot = df_y.nsmallest(1, "Happiness").iloc[0]
    r_val = safe_pearson_r(df_y[x_metric].values, df_y["Happiness"].values)
    r_str = f"{r_val:.2f}" if r_val is not None and np.isfinite(r_val) else "n/a"
    m1.metric(tr(lang, "kpi_global_mean"), f"{gavg:.2f}", delta=f"{tr(lang, 'kpi_year_prefix')} {year}")
    m2.metric(tr(lang, "kpi_n_countries"), f"{n_ct}")
    m3.metric(tr(lang, "kpi_highest"), f"{top['Happiness']:.2f}", delta=str(top["Country"])[:22])
    m4.metric(tr(lang, "kpi_lowest"), f"{bot['Happiness']:.2f}", delta=str(bot["Country"])[:22])

    st.divider()

    # --- Narrative row
    _title_with_tip(lang, tr(lang, "h_at_glance"), "tip_glance")
    st.info(
        tr(lang, "info_at_glance").format(
            year=year,
            n_ct=n_ct,
            x_label=x_label,
            r_str=r_str,
            assoc=tr(lang, "assoc_only"),
        )
    )
    _title_with_tip(lang, tr(lang, "insights_h"), "tip_insights_auto")
    for line in compute_insights(
        df,
        df_y,
        year,
        [],
        year_min,
        year_max,
        x_metric,
        x_label,
        lang,
    ):
        st.markdown(f"- {line}")

    if "Happiness_ci_low" in df_y.columns and "Happiness_ci_high" in df_y.columns:
        st.success(tr(lang, "ci_banner"))

    prev_y = df[df["Year"] == year - 1]
    global_avg = gavg
    prev_avg = prev_y["Happiness"].mean() if len(prev_y) else np.nan
    delta_txt = (
        tr(lang, "delta_vs_prior").format(delta=global_avg - prev_avg)
        if np.isfinite(prev_avg)
        else tr(lang, "na_prior_year")
    )
    fit = _safe_polyfit_deg1(df_y["GDP"].values, df_y["Happiness"].values)
    if fit is not None:
        pred = np.polyval(fit, df_y["GDP"].values)
    else:
        pred = np.full(len(df_y), float(df_y["Happiness"].mean()))
    resid = df_y["Happiness"].values - pred
    df_y = df_y.assign(_resid=resid)
    star = df_y.nlargest(1, "_resid").iloc[0]

    c1, c2 = st.columns(2)
    with c1:
        ex_l, ex_r = st.columns([0.88, 0.12])
        with ex_l:
            st.markdown(tr(lang, "h_exec_snapshot"))
        with ex_r:
            _inline_tip(lang, "tip_exec_snapshot")
        st.markdown(
            tr(lang, "exec_snapshot_md").format(
                year=year,
                gavg=global_avg,
                delta_txt=delta_txt,
                gdp_fit_label=gdp_fit_label,
                star=star["Country"],
                wh_source=wh_source,
            )
        )
    with c2:
        in_l, in_r = st.columns([0.88, 0.12])
        with in_l:
            st.markdown(tr(lang, "h_interp_notes"))
        with in_r:
            _inline_tip(lang, "tip_interp_notes")
        rng = df_y["Happiness"].max() - df_y["Happiness"].min()
        st.markdown(
            tr(lang, "interp_notes_md").format(
                year=year,
                rng=rng,
                x_label=x_label,
                r_str=r_str,
                star=star["Country"],
            )
        )

    st.divider()

    sm_l, sm_r = st.columns(2)
    with sm_l:
        sm_h, sm_t = st.columns([0.88, 0.12])
        with sm_h:
            st.markdown(tr(lang, "h_scatter_drivers"))
        with sm_t:
            _inline_tip(lang, "tip_scatter_chart")
    with sm_r:
        mp_h, mp_t = st.columns([0.88, 0.12])
        with mp_h:
            st.markdown(tr(lang, "h_map"))
        with mp_t:
            _inline_tip(lang, "tip_map")

    # Scatter
    fit_xy = _safe_polyfit_deg1(df_y[x_metric].values, df_y["Happiness"].values)
    if fit_xy is not None:
        line_x = np.linspace(
            float(np.nanmin(df_y[x_metric].values)),
            float(np.nanmax(df_y[x_metric].values)),
            80,
        )
        line_y = np.polyval(fit_xy, line_x)
    else:
        line_x = np.array([])
        line_y = np.array([])

    sc = go.Figure()
    _pop = df_y["Population"].astype(float)
    _pmax = float(np.nanmax(_pop.values))
    if not np.isfinite(_pmax) or _pmax <= 0:
        _sizes = np.full(len(df_y), 12.0)
    else:
        _sizes = np.clip(_pop / _pmax * 42 + 6, 6, 48)
    scatter_kwargs: dict = dict(
        x=df_y[x_metric],
        y=df_y["Happiness"],
        mode="markers",
        name="Countries",
        marker=dict(
            size=_sizes,
            color=df_y["Happiness"],
            colorscale="Viridis",
            colorbar=dict(title="Life evaluation", thickness=12, len=0.55, outlinewidth=0),
            line=dict(width=0.5, color="rgba(255,255,255,0.5)"),
        ),
        text=df_y["Country"],
        hovertemplate="<b>%{text}</b><br>Life evaluation: %{y:.2f}<extra></extra>",
    )
    if "Happiness_ci_low" in df_y.columns and "Happiness_ci_high" in df_y.columns:
        scatter_kwargs["error_y"] = dict(
            type="data",
            symmetric=False,
            array=df_y["Happiness_ci_high"] - df_y["Happiness"],
            arrayminus=df_y["Happiness"] - df_y["Happiness_ci_low"],
        )
    sc.add_trace(go.Scatter(**scatter_kwargs))
    if len(line_x) > 0 and fit_xy is not None:
        sc.add_trace(
            go.Scatter(
                x=line_x,
                y=line_y,
                mode="lines",
                name="Linear fit",
                line=dict(color="#312e81", width=2.2),
                hoverinfo="skip",
            )
        )
    sc.update_layout(
        title=f"Life evaluation vs selected driver · {year} · r ≈ {r_str}",
        height=_CROSS_ROW_PLOT_HEIGHT,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#fafbfc",
        xaxis_title=x_label,
        yaxis_title="Life evaluation (0–10)",
        yaxis=dict(range=[np.floor(happy_min), np.ceil(happy_max)]),
        margin=dict(t=50, l=8, r=8, b=8),
        annotations=[
            dict(
                text=f"{wh_source} · n = {n_ct}",
                xref="paper",
                yref="paper",
                x=0,
                y=-0.12,
                showarrow=False,
                font=dict(size=10, color="#64748b"),
            )
        ],
    )

    # Map
    mp = go.Figure(
        data=go.Choropleth(
            locations=df_y["iso_a3"],
            z=df_y["Happiness"],
            text=df_y["Country"],
            locationmode="ISO-3",
            colorscale="Viridis",
            zmin=happy_min,
            zmax=happy_max,
            marker_line_width=0.3,
            colorbar=dict(title="Life evaluation", thickness=12, len=0.5),
            hovertemplate="<b>%{text}</b><br>Life evaluation: %{z:.2f}<extra></extra>",
        )
    )
    mp.update_layout(
        title=f"Geographic distribution · {year}",
        height=_CROSS_ROW_PLOT_HEIGHT,
        geo=dict(
            showframe=False,
            projection_type="natural earth",
            projection_scale=1.12,
            bgcolor="#eef2ff",
            landcolor="#e2e8f0",
            showocean=True,
            oceancolor="#f8fafc",
        ),
        margin=dict(l=0, r=0, t=50, b=0),
    )

    iso_to_country = (
        df_y.drop_duplicates("iso_a3").set_index("iso_a3")["Country"].to_dict() if len(df_y) else {}
    )
    g1, g2 = st.columns(2)
    with g1:
        st.plotly_chart(sc, use_container_width=True, config=plotly_config())
    with g2:
        if HAS_PLOTLY_EVENTS and plotly_events is not None:
            st.caption(tr(lang, "map_click_hint"))
            ev = plotly_events(
                mp,
                click_event=True,
                key="map_click_events",
                override_height=_CROSS_ROW_PLOT_HEIGHT,
                override_width="100%",
            )
            if ev:
                for pt in ev:
                    loc = pt.get("location") or (pt.get("point") or {}).get("location")
                    if loc and loc in iso_to_country:
                        cname = iso_to_country[loc]
                        cur = list(st.session_state.get("trend_countries", []))
                        if cname not in cur and len(cur) < MAX_TREND_COUNTRIES:
                            cur.append(cname)
                            st.session_state.trend_countries = cur
        else:
            st.caption(tr(lang, "map_click_pkg"))
            st.plotly_chart(mp, use_container_width=True, config=plotly_config())

    # Histogram + bar
    mu = df_y["Happiness"].mean()
    hist = go.Figure(
        go.Histogram(
            x=df_y["Happiness"],
            nbinsx=26,
            marker_color="#6366f1",
            marker_line_color="#fff",
            marker_line_width=0.6,
            hovertemplate="Life evaluation: %{x:.2f}<br>Count: %{y}<extra></extra>",
        )
    )
    hist.add_vline(x=mu, line_dash="dash", line_color="#312e81", line_width=2)
    hist.update_layout(
        title=f"Distribution of life evaluations · {year} (dashed line = mean {mu:.2f})",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#fafbfc",
        xaxis_title="Life evaluation (0–10)",
        yaxis_title="Frequency",
        margin=dict(t=50, l=8, r=8, b=8),
        height=320,
    )

    rank = df_y.sort_values("Happiness", ascending=False)
    top_df = rank.head(rank_n).assign(seg="Top")
    bot_df = rank.tail(rank_n).assign(seg="Bottom")
    bar_df = pd.concat([top_df, bot_df], ignore_index=True)
    bar_df = bar_df.sort_values("Happiness")
    bar_df["color"] = bar_df["seg"].map({"Top": "#16a34a", "Bottom": "#ef4444"})

    br = go.Figure(
        go.Bar(
            x=bar_df["Happiness"],
            y=bar_df["Country"],
            orientation="h",
            marker_color=bar_df["color"],
            hovertemplate="<b>%{y}</b><br>Life evaluation: %{x:.2f}<extra></extra>",
        )
    )
    br.update_layout(
        title=f"Leaders vs laggards · Top {rank_n} / Bottom {rank_n} · {year}",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#fafbfc",
        xaxis_title="Life evaluation (0–10)",
        yaxis=dict(automargin=True, tickfont=dict(size=10)),
        margin=dict(l=8, r=12, t=50, b=40),
        height=max(380, rank_n * 22),
    )

    dh_l, dh_r = st.columns(2)
    with dh_l:
        dh_h, dh_t = st.columns([0.88, 0.12])
        with dh_h:
            st.markdown(tr(lang, "h_distribution"))
        with dh_t:
            _inline_tip(lang, "tip_histogram")
    with dh_r:
        rk_h, rk_t = st.columns([0.88, 0.12])
        with rk_h:
            st.markdown(tr(lang, "h_ranking"))
        with rk_t:
            _inline_tip(lang, "tip_rank_bars")

    g3, g4 = st.columns(2)
    with g3:
        st.plotly_chart(hist, use_container_width=True, config=plotly_config())
    with g4:
        st.plotly_chart(br, use_container_width=True, config=plotly_config())

    ex_l, ex_r = st.columns([0.88, 0.12])
    with ex_l:
        st.markdown(tr(lang, "h_export_preview"))
    with ex_r:
        _inline_tip(lang, "tip_export")

    exp1, exp2 = st.columns(2)
    with exp1:
        st.download_button(
            label=tr(lang, "dl_cross_section").format(year=year, n=n_ct),
            data=df_y.to_csv(index=False).encode("utf-8"),
            file_name=f"whr_cross_section_{year}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with exp2:
        with st.expander(tr(lang, "dl_preview"), expanded=False):
            st.dataframe(
                df_y[
                    ["Country", "Year", "Happiness", x_metric, "Population"]
                ].sort_values("Happiness", ascending=False),
                use_container_width=True,
                height=280,
            )

    st.divider()
    _title_with_tip(lang, tr(lang, "trend_h"), "tip_trend_section")
    st.caption(tr(lang, "trend_caption_intro").format(max_c=MAX_TREND_COUNTRIES))
    with st.expander("How dynamic presets are defined", expanded=False):
        st.markdown(
            """
| Preset | Definition |
|--------|------------|
| **Largest gain / decline** | Life evaluation in the **last** year minus the **first** year available for that country in this dataset (not necessarily every calendar year). |
| **Most volatile** | Highest **standard deviation** of annual life evaluations within the country (≥3 years required). |
| **Largest range** | Largest **max − min** of life evaluation within the country’s series. |
| **Outpaced / trailed global** | Country **(last − first)** minus **global mean (last − first)** over the same year range. |
| **Steepest slope** | OLS slope of life evaluation on **calendar year** (≥3 years). |

Geographic presets match **exact** country names in the file; unmatched names are skipped.
            """
        )

    _sync_trend_selection(countries)

    gg_l, gg_r = st.columns([0.88, 0.12])
    with gg_l:
        st.markdown(tr(lang, "h_geo_groups"))
    with gg_r:
        _inline_tip(lang, "tip_geo_presets")
    geo_a = st.columns(5)
    for col, label in zip(
        geo_a,
        ["Nordic", "G7", "Western EU", "Americas", "Asia–Pacific"],
    ):
        with col:
            if st.button(label, key=f"preset_geo_{label}", use_container_width=True):
                st.session_state.trend_countries = apply_preset(label, countries)
    geo_b = st.columns(4)
    for col, label in zip(
        geo_b,
        ["Benelux", "Baltic", "Southern EU", "English-speaking"],
    ):
        with col:
            if st.button(label, key=f"preset_geo_{label}", use_container_width=True):
                st.session_state.trend_countries = apply_preset(label, countries)

    st.markdown(tr(lang, "h_ref_year"))
    snap = st.columns(4)
    with snap[0]:
        if st.button(tr(lang, "btn_top5"), use_container_width=True, key="btn_top5"):
            st.session_state.trend_countries = (
                df_y.nlargest(5, "Happiness")["Country"].tolist()[:MAX_TREND_COUNTRIES]
            )
    with snap[1]:
        if st.button(tr(lang, "btn_bot5"), use_container_width=True, key="btn_bot5"):
            st.session_state.trend_countries = (
                df_y.nsmallest(5, "Happiness")["Country"].tolist()[:MAX_TREND_COUNTRIES]
            )
    with snap[2]:
        if st.button(tr(lang, "btn_clear"), use_container_width=True, key="btn_clear"):
            st.session_state.trend_countries = []
    with snap[3]:
        st.caption(tr(lang, "caption_n_countries").format(n=len(countries)))

    cd_l, cd_r = st.columns([0.88, 0.12])
    with cd_l:
        st.markdown(tr(lang, "h_change_dynamics"))
    with cd_r:
        _inline_tip(lang, "tip_dyn_presets")
    st.caption(
        f"Metrics use **{year_min}–{year_max}** in this extract. "
        "“vs global” compares each country’s start→end change to the global mean’s start→end change."
    )
    dyn_a = st.columns(4)
    with dyn_a[0]:
        if st.button(tr(lang, "dyn_gain"), use_container_width=True, key="dyn_gain"):
            st.session_state.trend_countries = trend_biggest_gains(df, MAX_TREND_COUNTRIES)
    with dyn_a[1]:
        if st.button(tr(lang, "dyn_loss"), use_container_width=True, key="dyn_loss"):
            st.session_state.trend_countries = trend_biggest_losses(df, MAX_TREND_COUNTRIES)
    with dyn_a[2]:
        if st.button(tr(lang, "dyn_vol"), use_container_width=True, key="dyn_vol"):
            st.session_state.trend_countries = trend_most_volatile(df, MAX_TREND_COUNTRIES)
    with dyn_a[3]:
        if st.button(tr(lang, "dyn_range"), use_container_width=True, key="dyn_range"):
            st.session_state.trend_countries = trend_largest_range(df, MAX_TREND_COUNTRIES)

    dyn_b = st.columns(4)
    with dyn_b[0]:
        if st.button(tr(lang, "dyn_beat"), use_container_width=True, key="dyn_beat"):
            st.session_state.trend_countries = trend_vs_global_delta_spread(df, MAX_TREND_COUNTRIES, beat=True)
    with dyn_b[1]:
        if st.button(tr(lang, "dyn_lag"), use_container_width=True, key="dyn_lag"):
            st.session_state.trend_countries = trend_vs_global_delta_spread(df, MAX_TREND_COUNTRIES, beat=False)
    with dyn_b[2]:
        if st.button(tr(lang, "dyn_slope_up"), use_container_width=True, key="dyn_slope_up"):
            st.session_state.trend_countries = trend_by_slope(df, MAX_TREND_COUNTRIES, positive=True)
    with dyn_b[3]:
        if st.button(tr(lang, "dyn_slope_dn"), use_container_width=True, key="dyn_slope_dn"):
            st.session_state.trend_countries = trend_by_slope(df, MAX_TREND_COUNTRIES, positive=False)

    st.markdown(tr(lang, "h_search_add"))
    q = st.text_input(
        tr(lang, "trend_search_label"),
        placeholder=tr(lang, "trend_search_ph"),
        key="trend_search_q",
        help=tr(lang, "help_trend_search"),
    )
    add_options = [c for c in sorted(countries) if q.strip() and q.lower() in c.lower()][:50]
    add_row = st.columns([2, 2, 1])
    with add_row[0]:
        if add_options:
            pick = st.selectbox(
                "Matching country",
                options=add_options,
                key="trend_add_pick",
                label_visibility="collapsed",
            )
        else:
            pick = None
            if q.strip():
                st.caption(tr(lang, "search_no_match"))
            else:
                st.caption(tr(lang, "search_prompt"))
    with add_row[1]:
        n_cur = len(st.session_state.get("trend_countries", []))
        at_cap = n_cur >= MAX_TREND_COUNTRIES
        can_add = pick is not None and not at_cap and pick not in st.session_state.get("trend_countries", [])
        if st.button(
            tr(lang, "trend_add"),
            use_container_width=True,
            key="btn_add_one",
            disabled=not can_add,
            help="Disabled if list is full, no match, or country already selected.",
        ):
            if can_add and pick:
                cur = list(st.session_state.trend_countries)
                cur.append(pick)
                st.session_state.trend_countries = cur[:MAX_TREND_COUNTRIES]
    with add_row[2]:
        if at_cap:
            st.caption(tr(lang, "list_full"))

    sel_countries = st.multiselect(
        tr(lang, "trend_multiselect_label"),
        options=sorted(countries),
        key="trend_countries",
        max_selections=MAX_TREND_COUNTRIES,
        help=tr(lang, "help_trend_multiselect"),
    )
    n_sel = len(sel_countries)
    st.caption(f"**{n_sel} / {MAX_TREND_COUNTRIES}** countries selected.")

    if not sel_countries:
        st.warning(tr(lang, "warn_pick_country"))
        try:
            if "c" in st.query_params:
                del st.query_params["c"]
        except Exception:
            pass
    else:
        df_l = df[df["Country"].isin(sel_countries)].sort_values(["Country", "Year"])
        glob = df.groupby("Year", as_index=False)["Happiness"].mean().rename(columns={"Happiness": "GlobalAvg"})

        tw0, tw1 = st.slider(
            "Years shown in trend chart (and in summary / export)",
            min_value=year_min,
            max_value=year_max,
            value=(year_min, year_max),
            key="trend_year_window",
            help=tr(lang, "help_trend_year_slider"),
        )
        try:
            st.query_params["t0"] = str(tw0)
            st.query_params["t1"] = str(tw1)
            st.query_params["c"] = "|".join(sel_countries)
        except Exception:
            pass

        sparse = sparse_country_warning(sel_countries, df, tw0, tw1)
        if sparse:
            st.warning(f"{tr(lang, 'sparse_warn')} {', '.join(sparse)}")

        df_l_plot = df_l[(df_l["Year"] >= tw0) & (df_l["Year"] <= tw1)].copy()
        glob_plot = glob[(glob["Year"] >= tw0) & (glob["Year"] <= tw1)].copy()

        fig = go.Figure()
        palette = (
            "#2563eb",
            "#dc2626",
            "#059669",
            "#d97706",
            "#7c3aed",
            "#db2777",
            "#0d9488",
            "#4f46e5",
        )
        for i, c in enumerate(sel_countries):
            sub = df_l_plot[df_l_plot["Country"] == c]
            fig.add_trace(
                go.Scatter(
                    x=sub["Year"],
                    y=sub["Happiness"],
                    mode="lines+markers",
                    name=c,
                    line=dict(width=2.2, color=palette[i % len(palette)]),
                    marker=dict(size=6),
                )
            )
        fig.add_trace(
            go.Scatter(
                x=glob_plot["Year"],
                y=glob_plot["GlobalAvg"],
                mode="lines",
                name="Global mean",
                line=dict(color="#64748b", dash="dash", width=2.4),
                hovertemplate="Global mean<br>Year %{x}<br>%{y:.2f}<extra></extra>",
            )
        )
        fig.update_layout(
            template="plotly_white",
            title=dict(text=f"Life evaluation vs global mean · {tw0}–{tw1}", font=dict(size=16)),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#fafbfc",
            yaxis=dict(range=[np.floor(happy_min), np.ceil(happy_max)], title="Life evaluation"),
            xaxis_title="Year",
            legend=dict(orientation="h", yanchor="bottom", y=-0.32, x=0.5, xanchor="center"),
            margin=dict(t=48, b=100),
            height=520,
            font=dict(family="Arial, sans-serif", size=12),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True, config=plotly_config_trend())

        trend_bullets = compute_insights(
            df,
            df_y,
            year,
            sel_countries,
            tw0,
            tw1,
            x_metric,
            x_label,
            lang,
            include_cross_section=False,
        )
        if trend_bullets:
            _title_with_tip(lang, tr(lang, "trend_insights_h"), "tip_insights_auto")
            for line in trend_bullets:
                st.markdown(f"- {line}")

        sum_df = trend_summary_table(df, sel_countries, tw0, tw1)
        if len(sum_df) > 0:
            su_l, su_r = st.columns([0.88, 0.12])
            with su_l:
                st.markdown(tr(lang, "h_summary_window"))
            with su_r:
                _inline_tip(lang, "tip_trend_summary")
            st.dataframe(sum_df, use_container_width=True)
            st.caption(tr(lang, "summary_foot"))

        trend_csv = df_l_plot[["Country", "Year", "Happiness"]].sort_values(["Country", "Year"]).to_csv(index=False)
        glob_csv = glob_plot.rename(columns={"GlobalAvg": "Global_mean_happiness"}).to_csv(index=False)
        dl1, dl2 = st.columns(2)
        with dl1:
            st.download_button(
                label="Download country series (CSV)",
                data=trend_csv.encode("utf-8"),
                file_name=f"whr_trend_countries_{tw0}_{tw1}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with dl2:
            st.download_button(
                label=tr(lang, "dl_trend_global"),
                data=glob_csv.encode("utf-8"),
                file_name=f"whr_trend_global_mean_{tw0}_{tw1}.csv",
                mime="text/csv",
                use_container_width=True,
            )

    st.divider()
    st.caption(wh_source)
    st.caption(tr(lang, "footer_disclaimer"))


if __name__ == "__main__":
    main()
