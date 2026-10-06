# VEC Bootstrap

**Put uncertainty bars around local VEC scores instead of over-interpreting one noisy number.**

`vec-bootstrap` repeatedly resamples cells **with replacement** from the prediction, pseudo-target, and reference/WT files, reruns the real public `veckit==0.1.2` scorer, and reports percentile confidence intervals for every numeric metric.

With two predictions, it performs a **paired comparison**: both models see the same bootstrap target/reference draw and the same scorer seed in each replicate. It then reports the fraction of bootstrap replicates in which model B beats model A using each ranking metric's actual direction (higher, lower, or zero-is-best).

## Why this is different from scorer-seed stability

Scorer seeds capture stochasticity inside the evaluation procedure. Bootstrap resampling asks a different question: **how much would this local metric move if the observed/generated cell samples were slightly different draws from the same underlying populations?**

Neither answers whether a model generalizes to the hidden test set.

## Usage

```bash
pip install -e .

# One-model uncertainty
vec-bootstrap model_a.h5ad   --task T1   --target pseudo_target.h5ad   --reference preceding_stage.h5ad   --reps 100   --out bootstrap_a

# Paired A/B comparison
vec-bootstrap model_a.h5ad   --prediction-b model_b.h5ad   --task T2 --setting heart   --target pseudo_target.h5ad   --reference preceding_stage.h5ad   --reps 100   --sample-cells 1500   --out bootstrap_compare
```

For T3, use `--wt matched_wt.h5ad`.

Outputs:

- `replicates.json` — every bootstrap scorer result;
- `summary.csv` — confidence intervals, SDs, paired improvement deltas and `bootstrap B-better fraction`;
- `report.md` — concise human-readable table.

## Statistical interpretation

The default 95% intervals are empirical percentile bootstrap intervals conditional on the files and pseudo-split you supplied. They estimate **cell-sampling variability**, not:

- model-training uncertainty;
- uncertainty from choosing a different pseudo-split;
- generalization to hidden validation/test targets;
- a formal competition-ranking probability.

For paired A/B comparison, target/reference resamples are shared to reduce nuisance variation. Prediction resamples are independent because the models define separate generated populations.

See `docs/SOURCES.md` for the scorer/task snapshot.
