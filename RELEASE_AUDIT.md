# Release audit

Release: **v1.0.0**  
Audit date: **2026-10-05**

## Release gate

GitHub Actions installs `anndata` and `veckit==0.1.2` on Python **3.10, 3.11, and 3.12** and runs:

- the complete pytest suite;
- a real synthetic H5AD paired-bootstrap scorer integration test;
- Ruff;
- bytecode compilation.

No Challenge data is bundled.

## Statistical coverage

Tests cover reproducible bootstrap resampling, empirical percentile intervals, higher/lower/zero-is-best metric directions, paired model comparison, and the descriptive bootstrap B-better fraction.

The documentation explicitly limits interpretation to cell-sampling variability on the supplied local files. It does not present the bootstrap fraction as a calibrated probability of hidden-test performance.

## Current verification

The latest public GitHub Actions matrix is green after the bootstrap-output terminology and regression-test updates.
