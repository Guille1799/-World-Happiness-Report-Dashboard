"""Five lines drawn on top of each other.

The trend chart fixed its y-axis to the whole dataset's range, 1 to 8. Pick the
five Nordic countries -- all between 7.2 and 7.9 -- and they came out as five
lines in the same place at the top of the frame. The chart existed to compare
them and made them indistinguishable.

`trend_y_range` fits the axis to what is actually plotted. The tests below pin
the two edges that a naive `min, max` gets wrong: a flat series, and values near
the ends of the 0-10 scale.
"""

from __future__ import annotations

from app import trend_y_range


def test_a_narrow_band_gets_a_narrow_axis():
    lo, hi = trend_y_range(7.2, 7.9)
    assert lo < 7.2 and hi > 7.9
    assert hi - lo < 1.5, "the axis is still far wider than the data: %r" % [lo, hi]


def test_a_flat_series_still_gets_a_visible_axis():
    """Every country at the same value: the span is 0, so a proportional pad
    would also be 0 and plotly would get a zero-height axis."""
    lo, hi = trend_y_range(6.5, 6.5)
    assert hi > lo
    assert hi - lo >= 0.3


def test_it_never_leaves_the_scale():
    """Life evaluation is a 0-10 ladder. The padding must not invent room
    outside it."""
    lo, _ = trend_y_range(0.05, 3.0)
    assert lo >= 0.0
    _, hi = trend_y_range(7.0, 9.98)
    assert hi <= 10.0


def test_the_arguments_can_arrive_backwards():
    assert trend_y_range(7.9, 7.2) == trend_y_range(7.2, 7.9)


def test_the_data_is_always_inside_the_range():
    for lo_in, hi_in in ((1.36, 7.86), (7.2, 7.9), (5.0, 5.0), (0.0, 10.0)):
        lo, hi = trend_y_range(lo_in, hi_in)
        assert lo <= lo_in and hi >= hi_in, (lo_in, hi_in, lo, hi)
