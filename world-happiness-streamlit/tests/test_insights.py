"""Tests for insights / correlation helpers."""

from __future__ import annotations

import numpy as np

from insights import safe_pearson_r


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
