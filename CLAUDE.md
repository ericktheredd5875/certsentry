# certsentry

Async CLI auditing TLS certificates. Full spec: @docs/PROJECT_BRIEF.md (source of truth for scope, architecture, milestones).

## How to work here
- Owner is a veteran PHP backend engineer learning Python; this is a public portfolio project. Code must be idiomatic, modern, fully typed Python.
- Scaffolding/tooling: do it fully. Core logic (fetch, checks, reporting): pair-program. Propose the design, stop for review, explain Python idioms (especially vs. PHP), review as a senior Python reviewer.
- Small changes, frequent commits with clear messages. Stop at the end of each milestone for review.
- Do not add dependencies without stating why.

## Commands
- `uv sync` / `uv run pytest` (live tests: `-m live`) / `uv run ruff check` / `uv run ruff format` / `uv run mypy`
- Quality gate before commit: ruff check, ruff format --check, mypy (strict), pytest.

## Architecture rules
- Network I/O only in `fetch.py`. Checks are pure functions `CertInfo -> list[Finding]`, no I/O.
- Models are frozen dataclasses; `Severity` is an ordered enum (worst = `max()`).
- Connection errors become results, never crashes. Exit codes: 0 ok, 1 warn, 2 crit/expired/invalid, 3 unreachable, 4 usage.
- Python 3.13+ (needs `get_unverified_chain()`); `src/` layout; pyproject only.
