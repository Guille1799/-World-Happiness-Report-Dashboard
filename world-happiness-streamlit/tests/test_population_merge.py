"""The map used to break on a good day.

`_attach_population_by_year` merges the population table into the happiness
panel. Both frames carry an `iso_a3` column, so pandas renamed the pair to
`iso_a3_x` / `iso_a3_y` and the column the choropleth reads disappeared.

The failure only appeared when the population table actually loaded, which
needs the network. With no network the code takes a different branch that keeps
the column, so the map worked offline and broke online. Nothing caught it:
`app.py` has no other test.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from app import _attach_population_by_year


def _panel() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Country": ["Spain", "Spain", "Finland"],
            "Year": [2019, 2023, 2023],
            "Happiness": [6.4, 6.5, 7.8],
            "iso_a3": ["ESP", "ESP", "FIN"],
        }
    )


def _population() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "iso_a3": ["ESP", "ESP", "FIN"],
            "Year": [2018, 2022, 2022],
            "Population": [46_800_000, 47_600_000, 5_500_000],
        }
    )


def test_iso_a3_survives_the_merge():
    """The column the map draws with has to still be there afterwards."""
    out = _attach_population_by_year(_panel(), _population())
    assert "iso_a3" in out.columns, (
        "iso_a3 vanished in the merge: pandas renamed the colliding pair to "
        "iso_a3_x / iso_a3_y, and the choropleth reads iso_a3"
    )
    assert "iso_a3_x" not in out.columns and "iso_a3_y" not in out.columns


def test_every_row_keeps_its_country_code():
    """Not one NaN. A silent NaN paints a blank country instead of raising."""
    out = _attach_population_by_year(_panel(), _population())
    assert out["iso_a3"].notna().all()
    assert set(out["iso_a3"]) == {"ESP", "FIN"}


def test_population_is_the_latest_year_at_or_before_the_row():
    """Backward merge-asof: 2019 takes 2018, 2023 takes 2022."""
    out = _attach_population_by_year(_panel(), _population()).set_index(
        ["iso_a3", "Year"]
    )
    assert out.loc[("ESP", 2019), "Population"] == 46_800_000
    assert out.loc[("ESP", 2023), "Population"] == 47_600_000


def test_a_country_with_no_population_row_keeps_its_code():
    """The empty-match branch must not drop iso_a3 either."""
    panel = _panel()
    pop = _population()
    pop = pop[pop["iso_a3"] != "FIN"]
    out = _attach_population_by_year(panel, pop)
    assert "iso_a3" in out.columns
    fin = out[out["iso_a3"] == "FIN"]
    assert len(fin) == 1
    assert np.isnan(fin["Population"].iloc[0])
