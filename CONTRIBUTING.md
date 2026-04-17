# Contributing to AutoTrader

## Local setup

1. Create and activate a virtual environment.
2. Install dependencies.
3. Run tests.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest -q
```

## Development rules

- Preserve risk controls by default.
- Keep live trading disabled by default in examples.
- Add or update tests for all behavior changes.
- Document new CLI flags and environment variables.

## Pull request checklist

- Add tests for new logic.
- Confirm CI passes.
- Note operational risks in the PR description.
