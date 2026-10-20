# certsentry

[![CI](https://github.com/ericktheredd5875/certsentry/actions/workflows/ci.yml/badge.svg)](https://github.com/ericktheredd5875/certsentry/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/ericktheredd5875/certsentry/graph/badge.svg)](https://codecov.io/gh/ericktheredd5875/certsentry)
[![PyPI](https://img.shields.io/pypi/v/certsentry)](https://pypi.org/project/certsentry/)
[![Python](https://img.shields.io/pypi/pyversions/certsentry)](https://pypi.org/project/certsentry/)
[![License: MIT](https://img.shields.io/pypi/l/certsentry)](LICENSE)

Async CLI that audits TLS certificates across many domains: expiry, chain,
hostname, and weak crypto. Cron- and CI-friendly exit codes.

> **Status:** early development. The `check` command is not implemented yet,
> and the examples below show the planned interface.
>
> certsentry is unrelated to Sentry.io.

## Planned usage

```bash
certsentry check example.com api.example.com:8443
certsentry check -f domains.txt --warn-days 30 --crit-days 14
cat domains.txt | certsentry check - --format json
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | All hosts OK |
| 1 | At least one WARN |
| 2 | At least one CRIT, EXPIRED, or invalid certificate |
| 3 | At least one host unreachable or erroring |
| 4 | Usage error |

## Development

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow.

## License

[MIT](LICENSE)
