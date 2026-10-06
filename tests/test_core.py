import numpy as np
import pytest

from vec_bootstrap.core import (
    bootstrap_indices,
    improvement_delta,
    interval,
    summarize,
)


def test_bootstrap_indices_sample_with_replacement_and_are_reproducible():
    a = bootstrap_indices(10, 100, np.random.default_rng(7))
    b = bootstrap_indices(10, 100, np.random.default_rng(7))
    assert np.array_equal(a, b)
    assert len(a) == 100
    assert len(set(a.tolist())) < 100


def test_interval():
    result = interval([1, 2, 3, 4], 0.5)
    assert result.mean == pytest.approx(2.5)
    assert result.low < result.mean < result.high


def test_directional_improvement():
    assert improvement_delta(0.2, 0.4, "higher") > 0
    assert improvement_delta(0.4, 0.2, "lower") > 0
    assert improvement_delta(-0.5, -0.1, "zero") > 0


def test_paired_summary_reports_bootstrap_win_fraction():
    records = [
        {
            "A": {"de_score": 0.2, "mmd_u": 0.4},
            "B": {"de_score": 0.3, "mmd_u": 0.3},
        },
        {
            "A": {"de_score": 0.1, "mmd_u": 0.5},
            "B": {"de_score": 0.4, "mmd_u": 0.2},
        },
    ]
    rows = {row["metric"]: row for row in summarize(records, "T1", 0.95)}
    assert rows["de_score"]["b_better_fraction"] == 1.0
    assert rows["mmd_u"]["b_better_fraction"] == 1.0
