# Contributing

Focused bug reports and pull requests are welcome. Never commit restricted Challenge data or held-out targets. Tests must use synthetic/shareable fixtures only.

Before opening a PR:

```bash
pip install -e '.[dev]'
pytest
ruff check src tests
python -m compileall -q src tests
```

Challenge-specific facts are snapshot-documented in `docs/SOURCES.md`; the official Challenge site remains authoritative.
