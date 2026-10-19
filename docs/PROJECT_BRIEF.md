# certsentry — Project Brief

> Hand this file to Claude at the start of the project. Save it in the repo as
> `docs/PROJECT_BRIEF.md` and ask Claude to create a `CLAUDE.md` from it.

## 1. Context (about me and why this exists)

- I'm a backend engineer with 20 years of experience, mostly in PHP. I've built
  data ingestion systems, a multi-tenant CMS from scratch, and an SSL proxy with
  automated certificate issuance and renewal for that CMS's tenant domains.
- I'm moving into Python professionally. This is my **first public Python
  portfolio project**. It needs to show **idiomatic, production-quality modern
  Python**, not PHP habits written in Python syntax.
- Hiring managers will read this repo. Code quality, tests, CI, packaging, and
  docs matter as much as the features.

## 2. How I want to work with you (Claude)

- **Set up the tooling and scaffolding completely**: project layout, pyproject,
  CI, configs.
- **For the core logic** (fetching certs, checks, reporting), work with me as a
  pair: propose the design, let me write it or write it together in small
  steps, and **explain Python idioms, especially where they differ from PHP**
  (dataclasses vs. arrays, context managers, generators, asyncio vs. PHP's
  synchronous model, typing, exceptions, packaging).
- Review my code like a senior Python reviewer and point out anything un-Pythonic.
- Keep changes small and commit often, with clear commit messages.
- Don't add dependencies without saying why.

## 3. What it is

`certsentry` is a CLI that audits TLS certificates for a list of domains,
**concurrently**, and reports problems in a form that works for humans, cron,
and CI pipelines.

```bash
certsentry check example.com api.example.com:8443
certsentry check -f domains.txt --warn-days 30 --crit-days 14
cat domains.txt | certsentry check - --format json
```

> **Name:** `certsentry` was free on PyPI as of 2026-10-19. Reserve it early by
> publishing a placeholder `0.0.1` release. Note: the README should make clear the
> project is unrelated to Sentry.io.

## 4. Tech stack

| Area | Choice |
|---|---|
| Python | **3.13+** (needed for `SSLSocket.get_verified_chain()` / `get_unverified_chain()`) |
| Project / env | **uv**, `src/` layout, `pyproject.toml` only (no setup.py) |
| CLI | **Typer** |
| Terminal output | **Rich** |
| Cert parsing | **cryptography** (x509) |
| Networking | stdlib `asyncio` + `ssl` |
| HTTP (alerts, v0.2) | **httpx** |
| Config / models | `dataclasses` for internal models; **pydantic** only for config file parsing (v0.2) |
| Lint / format | **ruff** (lint + format) |
| Types | **mypy --strict** (or pyright strict). The whole codebase is fully typed. |
| Tests | **pytest**, pytest-asyncio, pytest-cov, **trustme** (generates test CAs/certs) |
| Hooks | pre-commit (ruff, mypy) |
| CI | GitHub Actions |
| Release | PyPI via **Trusted Publishing** (OIDC, no API tokens), triggered by a git tag |
| License | MIT |

## 5. Features

### v0.1 (MVP, the first release)
- **Inputs:** domains as args, `-f/--file`, or `-` for stdin. Supports `host`,
  `host:port`, comments (`#`), and blank lines. Default port 443.
- **Concurrency:** asyncio with a `--concurrency` limit (default 20) and a
  per-host `--timeout` (default 10s).
- **SNI:** always sent.
- **Checks** (each one a small, pure, separately testable function):
  - Days until expiry → OK / WARN (`--warn-days`, default 30) / CRIT (`--crit-days`, default 14) / EXPIRED
  - Hostname matches the SAN entries (including wildcards)
  - Chain validates against the system trust store; detect self-signed certs
    and incomplete chains
  - Key type and size (flag RSA < 2048)
  - Signature algorithm (flag SHA-1)
  - Negotiated TLS version (flag below TLS 1.2)
- **Connection errors** (DNS failure, refused, timeout, handshake failure) are
  reported as results, never as crashes.
- **Output:** `--format table|json|markdown` (table is the default, rendered
  with Rich). JSON output gets a stable, documented schema.
- **Exit codes** (documented in the README):
  - `0`: all OK
  - `1`: at least one WARN
  - `2`: at least one CRIT, EXPIRED, or invalid
  - `3`: at least one host unreachable or erroring
  - `4`: usage error

### v0.2
- `--alert-webhook URL` and a Slack-formatted payload option
- A `certsentry.toml` config file (domains, thresholds, alerts)
- `--fail-on warn|crit` to tune exit behaviour in CI
- An example GitHub Actions workflow that runs certsentry on a schedule

### v0.3
- `certsentry mcp`: an MCP server mode so AI assistants can ask things like
  "which of my domains expire this month?"

## 6. Important design detail

To inspect a certificate that is **expired, self-signed, or for the wrong host**,
you can't rely on a verifying handshake, because it fails before you see the
cert. The approach:

1. Connect with a **non-verifying** SSL context to fetch the certificate and
   chain (`get_unverified_chain()`), the negotiated TLS version, and the cipher.
2. Determine chain validity **separately**: either a second verifying handshake,
   or capture the verification error from it (e.g.
   `ssl.SSLCertVerificationError.verify_message`).
3. Run all the checks on the parsed data. Checks never do network I/O.

Write this up as ADR-0001.

## 7. Suggested architecture

```
src/certsentry/
  __init__.py
  __main__.py      # python -m certsentry
  cli.py           # Typer app; parses args, calls the core, sets the exit code
  targets.py       # parses input lines -> Target(host, port)
  models.py        # Target, CertInfo, Finding, CheckResult, Severity (enum)
  fetch.py         # async TLS connection -> raw cert data (the only network I/O)
  checks.py        # pure functions: CertInfo -> list[Finding]
  runner.py        # concurrency (asyncio.Semaphore / TaskGroup), orchestration
  report/
    table.py  json.py  markdown.py
tests/
  unit/            # checks, target parsing, renderers, exit codes
  integration/     # local TLS servers with trustme-generated certs
  live/            # marked @pytest.mark.live, skipped by default
docs/
  PROJECT_BRIEF.md
  decisions/       # ADRs
```

Principles: network I/O is isolated in `fetch.py`, the checks are pure
functions, the models are typed (frozen dataclasses), and `Severity` is an
ordered enum so "worst result" is just `max()`.

## 8. Testing strategy

- **Unit tests:** cover every check using certificates generated in-test
  (trustme or cryptography): expired, nearly expired, wrong host, wildcard,
  weak key, SHA-1. Use `pytest.mark.parametrize` heavily.
- **Integration tests:** start a local TLS server (`asyncio.start_server` with
  an SSL context) serving each bad-cert scenario, then run the full pipeline
  against it. **No internet access needed in CI.**
- **Live tests** (opt-in, `pytest -m live`): run against badssl.com
  (`expired.badssl.com`, `self-signed.badssl.com`, `wrong.host.badssl.com`,
  `untrusted-root.badssl.com`, `sha256.badssl.com`).
- **CLI tests:** Typer's `CliRunner` for argument handling, output formats,
  and exit codes.
- Coverage target: about 90%. Report it in CI.

## 9. CI / release

- `ci.yml` runs on push and PR: `ruff check`, `ruff format --check`,
  `mypy --strict`, and `pytest --cov`, on Python 3.13 and 3.14, on ubuntu and
  windows.
- `release.yml` runs on a `v*` tag: build with `uv build`, publish to PyPI with
  Trusted Publishing, and create a GitHub Release with notes from CHANGELOG.
- README badges: CI status, coverage, PyPI version, Python versions, license.

## 10. Docs (the portfolio-facing part)

- **README:** a one-line pitch, a demo GIF or screenshot of the table output,
  install (`pipx install certsentry` / `uv tool install certsentry`), usage
  examples, the exit-code table, cron and GitHub Actions examples, the JSON
  schema, and a short **"Why I built this"** section about running TLS for a
  multi-tenant platform.
- **ADRs** in `docs/decisions/`: 0001 fetch-then-verify, 0002 asyncio over
  threads, 0003 exit code design.
- `CHANGELOG.md` in Keep a Changelog format, `CONTRIBUTING.md`, `LICENSE`.

## 11. Milestones

1. [ ] Scaffold: uv project, src layout, ruff/mypy/pytest configs, pre-commit, CI green on an empty test
2. [ ] `targets.py` + tests (input parsing)
3. [ ] `models.py` (Severity enum, dataclasses)
4. [ ] `fetch.py`: a single-host async fetch, run manually against a real site
5. [ ] `checks.py` + full unit test coverage
6. [ ] `runner.py`: concurrency, timeouts, errors turned into results
7. [ ] Renderers: table, json, markdown
8. [ ] CLI wiring and exit codes, plus CliRunner tests
9. [ ] Integration tests with local TLS servers
10. [ ] README, ADRs, CHANGELOG, demo GIF
11. [ ] Release workflow and **v0.1.0 on PyPI** 🎉
12. [ ] v0.2 → v0.3 (MCP)

## 12. Definition of done for v0.1

- `uv tool install certsentry && certsentry check github.com` works on a clean machine
- CI is green on all matrix targets, mypy strict has zero errors, coverage is ≥ 90%
- The README is good enough that a stranger can use the tool in 2 minutes
- A tagged release exists on PyPI and GitHub
