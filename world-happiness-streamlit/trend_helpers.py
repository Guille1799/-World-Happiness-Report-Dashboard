"""Pure functions for trend presets, rankings, and summary tables (unit-tested)."""

from __future__ import annotations

import numpy as np
import pandas as pd

MAX_TREND_COUNTRIES = 8

TREND_PRESETS: dict[str, list[str]] = {
    "Nordic": ["Finland", "Denmark", "Iceland", "Norway", "Sweden"],
    "G7": [
        "Canada",
        "France",
        "Germany",
        "Italy",
        "Japan",
        "United Kingdom",
        "United States",
    ],
    "Western EU": ["France", "Germany", "Italy", "Spain", "Netherlands", "Belgium", "Austria"],
    "Americas": ["United States", "Canada", "Brazil", "Mexico", "Argentina", "Chile", "Colombia"],
    "Asia–Pacific": ["Japan", "South Korea", "Australia", "New Zealand", "India", "China"],
    "Benelux": ["Belgium", "Netherlands", "Luxembourg"],
    "Baltic": ["Estonia", "Latvia", "Lithuania"],
    "Southern EU": ["Spain", "Portugal", "Italy", "Greece", "Malta", "Cyprus"],
    "English-speaking": [
        "United States",
        "United Kingdom",
        "Canada",
        "Australia",
        "New Zealand",
        "Ireland",
    ],
}


def apply_preset(preset_key: str, countries: list[str]) -> list[str]:
    avail = set(countries)
    out = [c for c in TREND_PRESETS.get(preset_key, []) if c in avail]
    return out[:MAX_TREND_COUNTRIES]


def trend_end_to_end_delta(df: pd.DataFrame) -> list[tuple[str, float]]:
    rows: list[tuple[str, float]] = []
    for c, g in df.groupby("Country"):
        g = g.sort_values("Year")
        if len(g) < 2:
            continue
        d = float(g["Happiness"].iloc[-1] - g["Happiness"].iloc[0])
        rows.append((c, d))
    return rows


def trend_biggest_gains(df: pd.DataFrame, n: int) -> list[str]:
    rows = trend_end_to_end_delta(df)
    rows.sort(key=lambda x: x[1], reverse=True)
    return [c for c, _ in rows[:n]]


def trend_biggest_losses(df: pd.DataFrame, n: int) -> list[str]:
    rows = trend_end_to_end_delta(df)
    rows.sort(key=lambda x: x[1], reverse=False)
    return [c for c, _ in rows[:n]]


def trend_most_volatile(df: pd.DataFrame, n: int) -> list[str]:
    rows: list[tuple[str, float]] = []
    for c, g in df.groupby("Country"):
        if len(g) < 3:
            continue
        rows.append((c, float(g["Happiness"].std(ddof=0))))
    rows.sort(key=lambda x: x[1], reverse=True)
    return [c for c, _ in rows[:n]]


def trend_largest_range(df: pd.DataFrame, n: int) -> list[str]:
    rows: list[tuple[str, float]] = []
    for c, g in df.groupby("Country"):
        if len(g) < 2:
            continue
        rows.append((c, float(g["Happiness"].max() - g["Happiness"].min())))
    rows.sort(key=lambda x: x[1], reverse=True)
    return [c for c, _ in rows[:n]]


def trend_vs_global_delta_spread(df: pd.DataFrame, n: int, beat: bool) -> list[str]:
    glob = df.groupby("Year", as_index=False)["Happiness"].mean().sort_values("Year")
    if len(glob) < 2:
        return []
    delta_g = float(glob["Happiness"].iloc[-1] - glob["Happiness"].iloc[0])
    rows: list[tuple[str, float]] = []
    for c, g in df.groupby("Country"):
        g = g.sort_values("Year")
        if len(g) < 2:
            continue
        dc = float(g["Happiness"].iloc[-1] - g["Happiness"].iloc[0])
        rows.append((c, dc - delta_g))
    rows.sort(key=lambda x: x[1], reverse=beat)
    return [c for c, _ in rows[:n]]


def trend_by_slope(df: pd.DataFrame, n: int, positive: bool) -> list[str]:
    rows: list[tuple[str, float]] = []
    for c, g in df.groupby("Country"):
        g = g.sort_values("Year")
        if len(g) < 3:
            continue
        years = g["Year"].astype(float).values
        y = g["Happiness"].values
        m, _ = np.polyfit(years, y, 1)
        rows.append((c, float(m)))
    rows.sort(key=lambda x: x[1], reverse=positive)
    return [c for c, _ in rows[:n]]


def calendar_years_in_range(y0: int, y1: int) -> set[int]:
    return set(range(y0, y1 + 1))


def trend_summary_table(df: pd.DataFrame, sel: list[str], y0: int, y1: int) -> pd.DataFrame:
    """Per-country stats within [y0, y1]; includes coverage vs full calendar span."""
    span = y1 - y0 + 1
    expected_years = calendar_years_in_range(y0, y1)
    rows: list[dict[str, object]] = []
    for c in sel:
        g = df[(df["Country"] == c) & (df["Year"] >= y0) & (df["Year"] <= y1)].sort_values("Year")
        if len(g) < 1:
            continue
        h = g["Happiness"]
        actual_years = set(g["Year"].astype(int).tolist())
        missing_n = len(expected_years - actual_years)
        coverage_pct = round(100.0 * len(actual_years) / span, 1) if span else 0.0
        rows.append(
            {
                "Country": c,
                "Years obs.": len(g),
                "Missing yrs*": missing_n,
                "Coverage %": coverage_pct,
                "First yr": int(g["Year"].iloc[0]),
                "Last yr": int(g["Year"].iloc[-1]),
                "First": round(float(h.iloc[0]), 3),
                "Last": round(float(h.iloc[-1]), 3),
                "Δ (last−first)": round(float(h.iloc[-1] - h.iloc[0]), 3),
                "Mean": round(float(h.mean()), 3),
                "σ": round(float(h.std(ddof=0)), 3) if len(h) > 1 else 0.0,
            }
        )
    return pd.DataFrame(rows)


def sparse_country_warning(sel: list[str], df: pd.DataFrame, y0: int, y1: int, min_years: int = 3) -> list[str]:
    """Country names with fewer than min_years observations in [y0,y1]."""
    bad: list[str] = []
    for c in sel:
        g = df[(df["Country"] == c) & (df["Year"] >= y0) & (df["Year"] <= y1)]
        if len(g) < min_years:
            bad.append(c)
    return bad
