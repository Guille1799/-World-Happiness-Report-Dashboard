"""Unit tests for trend_helpers (no Streamlit)."""

from __future__ import annotations

import pandas as pd
import pytest

from trend_helpers import (
    apply_preset,
    sparse_country_warning,
    trend_biggest_gains,
    trend_biggest_losses,
    trend_by_slope,
    trend_end_to_end_delta,
    trend_largest_range,
    trend_most_volatile,
    trend_summary_table,
    trend_vs_global_delta_spread,
)


@pytest.fixture
def tiny_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Country": ["A", "A", "A", "B", "B", "B"],
            "Year": [2020, 2021, 2022, 2020, 2021, 2022],
            "Happiness": [5.0, 5.5, 6.0, 7.0, 6.5, 6.0],
        }
    )


def test_apply_preset_filters_missing(tiny_df):
    countries = ["A", "B"]
    assert apply_preset("Nordic", countries) == []


def test_trend_biggest_gains(tiny_df):
    assert trend_biggest_gains(tiny_df, 1) == ["A"]


def test_trend_vs_global_beat(tiny_df):
    out = trend_vs_global_delta_spread(tiny_df, 2, beat=True)
    assert len(out) >= 1


def test_trend_summary_coverage(tiny_df):
    t = trend_summary_table(tiny_df, ["A"], 2020, 2022)
    assert len(t) == 1
    assert "Coverage %" in t.columns
    assert "Missing yrs*" in t.columns


def test_trend_by_slope(tiny_df):
    out = trend_by_slope(tiny_df, 2, positive=True)
    assert "A" in out or "B" in out


def test_trend_by_slope_negative(tiny_df):
    out = trend_by_slope(tiny_df, 2, positive=False)
    assert len(out) >= 1


def test_trend_end_to_end_delta_skips_short_series():
    df = pd.DataFrame({"Country": ["A"], "Year": [2020], "Happiness": [5.0]})
    assert trend_end_to_end_delta(df) == []


def test_trend_biggest_losses(tiny_df):
    assert trend_biggest_losses(tiny_df, 1) == ["B"]


def test_trend_most_volatile(tiny_df):
    out = trend_most_volatile(tiny_df, 2)
    assert len(out) >= 1


def test_trend_largest_range(tiny_df):
    out = trend_largest_range(tiny_df, 2)
    assert set(out) <= {"A", "B"}


def test_trend_vs_global_beat_false(tiny_df):
    out = trend_vs_global_delta_spread(tiny_df, 2, beat=False)
    assert isinstance(out, list)


def test_trend_vs_global_single_year_global():
    df = pd.DataFrame({"Country": ["A", "B"], "Year": [2020, 2020], "Happiness": [5.0, 6.0]})
    assert trend_vs_global_delta_spread(df, 2, beat=True) == []


def test_apply_preset_unknown_key():
    assert apply_preset("NonexistentPreset", ["Finland"]) == []


def test_trend_summary_empty_selection(tiny_df):
    assert len(trend_summary_table(tiny_df, [], 2020, 2022)) == 0


def test_trend_summary_single_row_country(tiny_df):
    one = pd.DataFrame({"Country": ["A"], "Year": [2020], "Happiness": [5.0]})
    t = trend_summary_table(one, ["A"], 2020, 2020)
    assert len(t) == 1
    assert float(t["σ"].iloc[0]) == 0.0


def test_sparse_country_warning(tiny_df):
    bad = sparse_country_warning(["A", "Missing"], tiny_df, 2020, 2022, min_years=3)
    assert "Missing" in bad
    assert "A" not in bad


def test_trend_most_volatile_skips_two_point_series():
    df = pd.DataFrame(
        {"Country": ["A", "A", "B", "B", "B"], "Year": [2020, 2021, 2020, 2021, 2022], "Happiness": [5.0, 5.1, 6.0, 5.0, 6.0]}
    )
    out = trend_most_volatile(df, 5)
    assert "B" in out


def test_trend_largest_range_skips_single_obs():
    df = pd.DataFrame({"Country": ["A"], "Year": [2020], "Happiness": [5.0]})
    assert trend_largest_range(df, 3) == []


def test_trend_vs_global_skips_short_country_series():
    df = pd.DataFrame(
        {
            "Country": ["A", "A", "B", "B", "B"],
            "Year": [2020, 2021, 2020, 2021, 2022],
            "Happiness": [5.0, 5.1, 6.0, 5.5, 6.0],
        }
    )
    assert len(trend_vs_global_delta_spread(df, 3, beat=True)) >= 1


def test_trend_vs_global_skips_single_row_country():
    df = pd.DataFrame(
        {"Country": ["Lonely", "B", "B"], "Year": [2020, 2020, 2021], "Happiness": [5.0, 6.0, 6.1]}
    )
    out = trend_vs_global_delta_spread(df, 2, beat=True)
    assert "B" in out


def test_trend_by_slope_skips_two_point_series():
    df = pd.DataFrame({"Country": ["A", "A"], "Year": [2020, 2021], "Happiness": [5.0, 5.1]})
    assert trend_by_slope(df, 3, positive=True) == []


def test_trend_summary_skips_country_with_no_rows():
    df = pd.DataFrame({"Country": ["A"], "Year": [2020], "Happiness": [5.0]})
    assert len(trend_summary_table(df, ["Nobody"], 2020, 2022)) == 0
