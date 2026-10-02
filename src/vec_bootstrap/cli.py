from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

import numpy as np

from .core import bootstrap_indices, summarize, write_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bootstrap uncertainty for local VEC pseudo-target scoring."
    )
    parser.add_argument("prediction_a", type=Path)
    parser.add_argument("--prediction-b", type=Path)
    parser.add_argument("--task", required=True, choices=["T1", "T2", "T3"])
    parser.add_argument("--setting", default="heart", choices=["heart", "embryo"])
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--wt", type=Path)
    parser.add_argument("--reps", type=int, default=100)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--sample-cells", type=int)
    parser.add_argument("--confidence", type=float, default=0.95)
    parser.add_argument("--out", type=Path, default=Path("bootstrap_out"))
    return parser


def _write_resample(
    data,
    path: Path,
    rng: np.random.Generator,
    sample_cells: int | None,
) -> None:
    index = bootstrap_indices(data.n_obs, sample_cells, rng)
    data[index].copy().write_h5ad(path)


def _score(
    score,
    task: str,
    prediction: Path,
    target: Path,
    reference: Path | None,
    wt: Path | None,
    setting: str,
    scorer_seed: int,
) -> dict:
    kwargs = {
        "task": task,
        "input": prediction,
        "target": target,
        "seed": scorer_seed,
    }
    if task in {"T1", "T2"}:
        kwargs["reference"] = reference
    if task == "T2":
        kwargs["setting"] = setting
    if task == "T3":
        kwargs["wt"] = wt
    return score(**kwargs)["metrics"]


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.reps < 2:
        raise SystemExit("--reps must be >= 2")
    if args.sample_cells is not None and args.sample_cells <= 0:
        raise SystemExit("--sample-cells must be > 0")
    if not 0 < args.confidence < 1:
        raise SystemExit("--confidence must be between 0 and 1")
    if args.task in {"T1", "T2"} and args.reference is None:
        raise SystemExit("--reference is required for T1/T2")
    if args.task == "T3" and args.wt is None:
        raise SystemExit("--wt is required for T3")

    import anndata as ad
    from veckit import score

    pred_a = ad.read_h5ad(args.prediction_a)
    pred_b = ad.read_h5ad(args.prediction_b) if args.prediction_b else None
    target = ad.read_h5ad(args.target)
    reference = ad.read_h5ad(args.reference) if args.reference else None
    wt = ad.read_h5ad(args.wt) if args.wt else None

    args.out.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        for rep in range(args.reps):
            base = np.random.SeedSequence([args.seed, rep])
            child = base.spawn(5)
            target_path = root / "target.h5ad"
            ref_path = root / "reference.h5ad"
            wt_path = root / "wt.h5ad"
            a_path = root / "a.h5ad"
            b_path = root / "b.h5ad"

            _write_resample(
                target,
                target_path,
                np.random.default_rng(child[0]),
                args.sample_cells,
            )
            if reference is not None:
                _write_resample(
                    reference,
                    ref_path,
                    np.random.default_rng(child[1]),
                    args.sample_cells,
                )
            if wt is not None:
                _write_resample(
                    wt,
                    wt_path,
                    np.random.default_rng(child[1]),
                    args.sample_cells,
                )
            _write_resample(
                pred_a,
                a_path,
                np.random.default_rng(child[2]),
                args.sample_cells,
            )
            if pred_b is not None:
                _write_resample(
                    pred_b,
                    b_path,
                    np.random.default_rng(child[3]),
                    args.sample_cells,
                )

            scorer_seed = int(args.seed + rep)
            a_metrics = _score(
                score,
                args.task,
                a_path,
                target_path,
                ref_path if reference is not None else None,
                wt_path if wt is not None else None,
                args.setting,
                scorer_seed,
            )
            b_metrics = None
            if pred_b is not None:
                b_metrics = _score(
                    score,
                    args.task,
                    b_path,
                    target_path,
                    ref_path if reference is not None else None,
                    wt_path if wt is not None else None,
                    args.setting,
                    scorer_seed,
                )
            records.append(
                {
                    "replicate": rep,
                    "scorer_seed": scorer_seed,
                    "A": a_metrics,
                    "B": b_metrics,
                }
            )

    rows = summarize(records, args.task, args.confidence)
    (args.out / "replicates.json").write_text(
        json.dumps(records, indent=2, default=float) + "\n"
    )
    write_csv(rows, args.out / "summary.csv")

    lines = [
        "# VEC Bootstrap",
        "",
        (
            f"Replicates: **{args.reps}** · confidence interval: "
            f"**{args.confidence:.1%}**"
        ),
        "",
        (
            "> Bootstrap intervals quantify sampling variability on this local "
            "pseudo-split. They do not measure training uncertainty or "
            "hidden-test generalization."
        ),
        "",
        "| metric | direction | A mean [CI] | B mean [CI] | P(B better) |",
        "|---|---|---|---|---:|",
    ]
    for row in rows:
        a = (
            f"{row['a_mean']:.5g} "
            f"[{row['a_low']:.5g}, {row['a_high']:.5g}]"
        )
        if "b_mean" in row:
            b = (
                f"{row['b_mean']:.5g} "
                f"[{row['b_low']:.5g}, {row['b_high']:.5g}]"
            )
            p = (
                f"{row.get('p_b_better', float('nan')):.3f}"
                if "p_b_better" in row
                else "—"
            )
        else:
            b, p = "—", "—"
        lines.append(
            f"| {row['metric']} | {row['direction']} | {a} | {b} | {p} |"
        )
    (args.out / "report.md").write_text("\n".join(lines) + "\n")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
