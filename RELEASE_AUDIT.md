# Release audit

Release: **v1.0.0**  
Audit date: **2026-10-01**

Core bootstrap/statistical logic is covered by local unit tests. GitHub Actions installs `anndata` and `veckit==0.1.2` on Python 3.10/3.11/3.12 and runs a real synthetic H5AD paired-bootstrap scorer integration test, pytest, Ruff, and compileall. No Challenge data is bundled.

## Current verification

Local: 4/4 dependency-free statistical/unit tests passing; the real-scorer integration test is included and runs in CI where dependencies can be installed.
All Python source compiles successfully in the release workspace.
