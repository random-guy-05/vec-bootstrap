# Statistical interpretation of VEC Bootstrap

## What is resampled

For each replicate, the tool independently resamples cells with replacement from:

- model A prediction;
- model B prediction, if supplied;
- the pseudo-target;
- the preceding reference (T1/T2) or matched WT (T3).

In an A/B comparison, the target/reference resamples and scorer seed are **shared** between models within a replicate. Prediction resamples are separate. This paired design reduces nuisance variation from the evaluation sample when the question is whether B is consistently better than A.

## Confidence intervals

The reported interval is an empirical percentile bootstrap interval. With the default 95% confidence level, it is the 2.5th to 97.5th percentile of bootstrap metric values.

For a ranking metric in A/B mode, VEC Bootstrap also computes an **improvement-oriented paired delta**:

- higher-is-better: `B - A`;
- lower-is-better: `A - B`;
- zero-is-best: `abs(A) - abs(B)`.

Positive means B improved under the official metric direction. `bootstrap B-better fraction` is the fraction of paired bootstrap replicates whose improvement-oriented delta is positive. It is a descriptive bootstrap frequency, **not a calibrated probability of winning the hidden leaderboard**.

## What the interval does not include

It does not capture:

- retraining the model with a different random seed;
- changing the pseudo-holdout split;
- uncertainty from hyperparameter/model selection;
- domain shift to validation/test targets;
- uncertainty in the competition's hidden ranking.

## Practical recommendations

- 30-50 reps: quick debugging only.
- 100 reps: useful routine comparison.
- 500+ reps: more stable tail intervals when runtime permits.
- Keep the same `--sample-cells` across models when comparing them.
- Use the full default cell count when you specifically want uncertainty at the exported population size.
