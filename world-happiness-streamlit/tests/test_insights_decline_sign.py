"""The panel called a rise a decline.

`compute_insights` picks the country with the smallest change in the window and
announced it as the "Largest decline". It never checked the sign. When every
selected country improved, the one that improved least was labelled a decline —
with a positive delta printed right beside the word.
"""

from __future__ import annotations

import pandas as pd

from insights import compute_insights


def _panel(deltas: dict[str, tuple[float, float]]) -> pd.DataFrame:
    """One row per country per year: (value in 2020, value in 2024)."""
    rows = []
    for country, (start, end) in deltas.items():
        rows.append({"Country": country, "Year": 2020, "Happiness": start, "GDP": 10.0})
        rows.append({"Country": country, "Year": 2024, "Happiness": end, "GDP": 10.5})
    return pd.DataFrame(rows)


def _lines(deltas: dict[str, tuple[float, float]], lang: str = "en") -> str:
    df = _panel(deltas)
    df_y = df[df["Year"] == 2024]
    return " ".join(
        compute_insights(
            df, df_y, 2024, list(deltas), 2020, 2024, "GDP", "Log GDP", lang,
            include_cross_section=False,
        )
    )


def test_everyone_rose_so_nobody_declined():
    """+0.60 and +0.10 are both gains. Neither is a decline."""
    out = _lines({"Finland": (7.0, 7.6), "Spain": (6.0, 6.1)})
    assert "decline" not in out.lower(), (
        f"the smallest gain was announced as a decline: {out!r}"
    )
    assert "smallest **gain**" in out.lower() or "smallest gain" in out.lower()


def test_a_real_fall_is_still_called_a_decline():
    """The counterweight: dodging the word must not mean never using it."""
    out = _lines({"Finland": (7.0, 7.6), "Spain": (6.0, 5.4)})
    assert "decline" in out.lower()
    assert "smallest" not in out.lower()


def test_the_sign_printed_matches_the_word():
    """A negative delta next to 'gain', or a positive one next to 'decline',
    is the same bug wearing the other hat."""
    for deltas in ({"A": (7.0, 7.6), "B": (6.0, 6.1)}, {"A": (7.0, 7.6), "B": (6.0, 5.4)}):
        out = _lines(deltas)
        if "decline" in out.lower():
            assert "≈ -" in out or "≈ −" in out, out
        else:
            assert "≈ +" in out, out


def test_spanish_says_it_too():
    out = _lines({"Finland": (7.0, 7.6), "Spain": (6.0, 6.1)}, lang="es")
    assert "caída" not in out.lower()
    assert "menor **subida**" in out.lower() or "menor subida" in out.lower()
