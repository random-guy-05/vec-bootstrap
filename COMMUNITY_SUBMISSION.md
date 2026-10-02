# Community Contribution submission text

## Title
VEC Bootstrap — bootstrap confidence intervals and paired uncertainty for local VEC metrics

## Description
VEC Bootstrap adds uncertainty quantification to local VEC model selection. It repeatedly resamples cells with replacement from prediction, pseudo-target and reference/WT H5ADs, reruns the real public `veckit==0.1.2` scorer, and reports empirical confidence intervals for every numeric metric. With two predictions it performs a paired comparison: both candidates share the same target/reference bootstrap draw and scorer seed, while their generated-cell populations are resampled independently. It then reports direction-aware paired improvement intervals and the fraction of replicates in which model B is better for each official ranking metric, including zero-is-best terms. The documentation explicitly distinguishes cell-sampling uncertainty from training uncertainty or hidden-test generalization. It helps teams avoid over-interpreting tiny differences between single local scores.
