"""Tests for insights / correlation helpers."""

from __future__ import annotations

from unittest.mock import patch

import numpy as np
import pandas as pd

from insights import compute_insights, safe_pearson_r


def test_safe_pearson_r_perfect_line():
    x = np.array([1.0, 2.0, 3.0, 4.0])
    y = np.array([2.0, 4.0, 6.0, 8.0])
    r = safe_pearson_r(x, y)
    assert r is not None
    assert abs(r - 1.0) < 1e-9


def test_safe_pearson_r_zero_variance_x():
    assert safe_pearson_r([1.0, 1.0, 1.0], [1.0, 2.0, 3.0]) is None


def test_safe_pearson_r_too_few_points():
    assert safe_pearson_r([1.0], [2.0]) is None


def test_safe_pearson_r_nonfinite_result():
    with patch("numpy.corrcoef", side_effect=RuntimeError("boom")):
        assert safe_pearson_r([1.0, 2.0, 3.0], [3.0, 2.0, 1.0]) is None


def _df_trend() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Country": ["X", "X", "X", "Y", "Y", "Y", "Z", "Z", "Z"],
            "Year": [2020, 2021, 2022] * 3,
            "Happiness": [5.0, 5.5, 6.2, 7.0, 6.0, 5.0, 6.0, 6.1, 6.2],
        }
    )


def test_compute_insights_too_few_countries_cross_section():
    df = _df_trend()
    df_y = df[df["Year"] == 2022].head(2)
    out = compute_insights(df, df_y, 2022, [], 2020, 2022, "GDP", "GDP", lang="en")
    assert out == []


def test_compute_insights_trend_only_empty_selection():
    df = _df_trend()
    df_y = df[df["Year"] == 2022]
    out = compute_insights(
        df, df_y, 2022, [], 2020, 2022, "GDP", "GDP", lang="en", include_cross_section=False
    )
    assert out == []


def test_compute_insights_pearson_na_en():
    df = _df_trend()
    df_y = pd.DataFrame(
        {
            "Country": ["A", "B", "C"],
            "Happiness": [5.0, 5.0, 5.0],
            "GDP": [1.0, 2.0, 3.0],
        }
    )
    out = compute_insights(df, df_y, 2022, ["X"], 2020, 2022, "GDP", "GDP", lang="en")
    assert any("n/a" in line.lower() or "not defined" in line.lower() for line in out)


def test_compute_insights_pearson_na_es():
    df = _df_trend()
    df_y = pd.DataFrame(
        {
            "Country": ["A", "B", "C"],
            "Happiness": [5.0, 5.0, 5.0],
            "GDP": [1.0, 2.0, 3.0],
        }
    )
    out = compute_insights(df, df_y, 2022, ["X"], 2020, 2022, "GDP", "PIB", lang="es")
    assert any("no definida" in line.lower() for line in out)


def test_compute_insights_correlation_and_top_en():
    df = _df_trend()
    df_y = pd.DataFrame(
        {
            "Country": ["A", "B", "C"],
            "Happiness": [5.0, 7.0, 6.0],
            "GDP": [1.0, 3.0, 2.0],
        }
    )
    out = compute_insights(df, df_y, 2022, [], 2020, 2022, "GDP", "GDP", lang="en")
    assert any("Pearson" in line for line in out)
    assert any("Highest" in line for line in out)
    assert any("spread" in line.lower() or "ladder" in line.lower() for line in out)


def test_compute_insights_correlation_es():
    df = _df_trend()
    df_y = pd.DataFrame(
        {
            "Country": ["A", "B", "C"],
            "Happiness": [5.0, 7.0, 6.0],
            "GDP": [1.0, 3.0, 2.0],
        }
    )
    out = compute_insights(df, df_y, 2022, [], 2020, 2022, "GDP", "PIB", lang="es")
    assert any("Pearson" in line or "correlación" in line for line in out)


def test_compute_insights_trend_picks_en_es():
    df = _df_trend()
    df_y = df[df["Year"] == 2022]
    out_en = compute_insights(
        df, df_y, 2022, ["X", "Y"], 2020, 2022, "GDP", "GDP", lang="en", include_cross_section=False
    )
    assert any("improvement" in line.lower() or "decline" in line.lower() for line in out_en)
    out_es = compute_insights(
        df, df_y, 2022, ["X", "Y"], 2020, 2022, "GDP", "PIB", lang="es", include_cross_section=False
    )
    assert any("mejora" in line.lower() or "caída" in line.lower() for line in out_es)


def test_compute_insights_trend_only_no_cross():
    df = _df_trend()
    df_y = df[df["Year"] == 2022]
    out = compute_insights(
        df, df_y, 2022, ["X", "Y"], 2020, 2022, "GDP", "GDP", lang="en", include_cross_section=False
    )
    assert not any("Pearson" in line for line in out)
    assert any("improvement" in line.lower() for line in out)


def test_compute_insights_skips_country_with_few_years_in_window():
    df = pd.DataFrame(
        {
            "Country": ["OnlyOne", "X", "X", "X"],
            "Year": [2022, 2020, 2021, 2022],
            "Happiness": [5.0, 5.0, 5.5, 6.0],
        }
    )
    df_y = pd.DataFrame(
        {"Country": ["A", "B", "C"], "Happiness": [5.0, 7.0, 6.0], "GDP": [1.0, 3.0, 2.0]}
    )
    out = compute_insights(df, df_y, 2022, ["OnlyOne", "X"], 2020, 2022, "GDP", "GDP", lang="en")
    assert any("improvement" in line.lower() for line in out)


def test_compute_insights_no_decline_when_same_best_worst():
    df = pd.DataFrame(
        {
            "Country": ["Same", "Same", "Same"],
            "Year": [2020, 2021, 2022],
            "Happiness": [6.0, 6.1, 6.2],
        }
    )
    df_y = pd.DataFrame(
        {"Country": ["A", "B", "C"], "Happiness": [5.0, 7.0, 6.0], "GDP": [1.0, 3.0, 2.0]}
    )
    out = compute_insights(df, df_y, 2022, ["Same"], 2020, 2022, "GDP", "GDP", lang="en")
    assert not any("decline" in line.lower() for line in out)


def test_compute_insights_caps_at_five_lines():
    df = _df_trend()
    df_y = pd.DataFrame(
        {
            "Country": ["A", "B", "C", "D"],
            "Happiness": [4.0, 8.0, 6.0, 5.0],
            "GDP": [1.0, 4.0, 2.0, 3.0],
        }
    )
    out = compute_insights(df, df_y, 2022, ["X", "Y", "Z"], 2020, 2022, "GDP", "GDP", lang="en")
    assert len(out) <= 5
