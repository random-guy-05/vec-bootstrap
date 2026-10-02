from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

RANKING_DIRECTIONS = {
    "T1": {
        "de_score": "higher",
        "de_direction": "higher",
        "mmd_u": "lower",
        "variogram": "lower",
    },
    "T2": {
        "de_score": "higher",
        "de_direction": "higher",
        "mmd_u": "lower",
        "variogram": "lower",
        "d2_shape": "lower",
        "occupancy_dice": "higher",
        "scale_log_ratio": "zero",
        "neighborhood_mmd": "lower",
    },
    "T3": {
        "de_score": "higher",
        "de_direction": "higher",
        "severity_slope": "zero",
        "mmd_u": "lower",
        "variogram": "lower",
    },
}


@dataclass(frozen=True)
class Interval:
    mean: float
    low: float
    high: float
    sd: float


def numeric(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def bootstrap_indices(
    n_cells: int,
    sample_cells: int | None,
    rng: np.random.Generator,
) -> np.ndarray:
    if n_cells <= 0:
        raise ValueError("dataset must contain at least one cell")
    count = n_cells if sample_cells is None else sample_cells
    if count <= 0:
        raise ValueError("sample_cells must be positive")
    return rng.integers(0, n_cells, size=count, endpoint=False)


def interval(values: list[float], confidence: float = 0.95) -> Interval:
    if not values:
        raise ValueError("cannot summarize an empty sample")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
    array = np.asarray(values, dtype=float)
    alpha = 1.0 - confidence
    low, high = np.quantile(array, [alpha / 2, 1 - alpha / 2])
    return Interval(
        mean=float(array.mean()),
        low=float(low),
        high=float(high),
        sd=float(array.std(ddof=1)) if len(array) > 1 else 0.0,
    )


def improvement_delta(a: float, b: float, direction: str) -> float:
    if direction == "higher":
        return b - a
    if direction == "lower":
        return a - b
    if direction == "zero":
        return abs(a) - abs(b)
    raise ValueError(f"unknown direction: {direction}")


def summarize(
    records: list[dict],
    task: str,
    confidence: float = 0.95,
) -> list[dict]:
    task = task.upper()
    directions = RANKING_DIRECTIONS[task]
    metric_names = sorted(
        {
            name
            for record in records
            for model in ("A", "B")
            if record.get(model)
            for name in record[model]
            if not str(name).startswith("_")
        }
    )
    rows: list[dict] = []
    for metric in metric_names:
        a_values = [
            n
            for record in records
            if record.get("A")
            if (n := numeric(record["A"].get(metric))) is not None
        ]
        b_values = [
            n
            for record in records
            if record.get("B")
            if (n := numeric(record["B"].get(metric))) is not None
        ]
        if not a_values:
            continue
        a_int = interval(a_values, confidence)
        row = {
            "metric": metric,
            "direction": directions.get(metric, "diagnostic"),
            "a_mean": a_int.mean,
            "a_low": a_int.low,
            "a_high": a_int.high,
            "a_sd": a_int.sd,
        }
        if b_values:
            b_int = interval(b_values, confidence)
            row.update(
                b_mean=b_int.mean,
                b_low=b_int.low,
                b_high=b_int.high,
                b_sd=b_int.sd,
            )
            direction = directions.get(metric)
            if direction:
                paired = []
                raw_delta = []
                for record in records:
                    a = numeric((record.get("A") or {}).get(metric))
                    b = numeric((record.get("B") or {}).get(metric))
                    if a is None or b is None:
                        continue
                    raw_delta.append(b - a)
                    paired.append(improvement_delta(a, b, direction))
                if paired:
                    p_int = interval(paired, confidence)
                    r_int = interval(raw_delta, confidence)
                    row.update(
                        improvement_mean=p_int.mean,
                        improvement_low=p_int.low,
                        improvement_high=p_int.high,
                        raw_delta_mean=r_int.mean,
                        raw_delta_low=r_int.low,
                        raw_delta_high=r_int.high,
                        p_b_better=float(np.mean(np.asarray(paired) > 0)),
                    )
        rows.append(row)
    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    fields = sorted(
        {key for row in rows for key in row},
        key=lambda x: (x != "metric", x),
    )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
