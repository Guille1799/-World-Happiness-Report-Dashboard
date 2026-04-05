"""Unit tests for trend_helpers (no Streamlit)."""

from __future__ import annotations

import pandas as pd
import pytest

from trend_helpers import (
    apply_preset,
    trend_biggest_gains,
    trend_by_slope,
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
