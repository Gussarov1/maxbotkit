# Contributing

Thanks for helping improve `maxbotkit`.

## Development setup

1. Create and activate a virtual environment.
2. Install the project in editable mode:

```bash
python -m pip install -e .[dev] --no-build-isolation
```

## Local checks

Before opening a pull request, run:

```bash
env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests
python -m ruff check .
python -m mypy src
```

## Pull requests

- Keep pull requests focused and small when possible.
- Add or update tests for behavior changes.
- Update `README.md` or `CHANGELOG.md` when user-facing behavior changes.
- Prefer typed interfaces and explicit error handling.

## Release checklist

For manual releases:

```bash
python -m pip install -e '.[dev]' --no-build-isolation
env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests
python -m ruff check .
python -m mypy src
rm -rf build dist
python -m build
python -m twine check dist/*
```

## Design direction

The project aims for:

- async-first architecture
- aiogram-like developer experience
- production-minded reliability and observability
- compatibility with open and closed network environments
