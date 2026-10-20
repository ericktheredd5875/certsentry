# Contributing

## Setup

Requires [uv](https://docs.astral.sh/uv/) and Python 3.13+.

```bash
uv sync
uv run pre-commit install
```

## Before opening a PR

CI runs all of these. Run them locally first:

```bash
uv run ruff check
uv run ruff format --check
uv run mypy
uv run pytest --cov
```

Coverage must stay at or above 90%.

## Conventions

- The codebase is fully typed and passes `mypy --strict`.
- Network I/O lives only in `fetch.py`. Checks are pure functions that take
  parsed certificate data and return findings.
- Do not add a dependency without a clear reason, and state it in the PR.
- Tests that need the internet are marked `live` and skipped by default.
  Run them with `uv run pytest -m live`.

## Commits and PRs

- Keep changes small and focused, with a clear commit message.
- Add a line under `[Unreleased]` in `CHANGELOG.md` for user-visible changes.
