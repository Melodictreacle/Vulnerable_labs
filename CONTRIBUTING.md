# Contributing & DevOps Pipeline

This repository ships **intentionally vulnerable** lab environments and
first-party Python exploit clients. The CI pipeline reflects that: it does **not**
scan the lab images for CVEs (they are vulnerable by design) — it keeps the
*tooling* honest.

## What CI checks

Defined in [.github/workflows/ci.yml](.github/workflows/ci.yml) and run on every
push / pull request to `main`:

| Job | Tool | What it enforces |
|---|---|---|
| `python-lint` | [ruff](https://docs.astral.sh/ruff/) | Lint the exploit clients (undefined names, unused imports, f-string bugs). Config in `pyproject.toml`. |
| `python-compile` | `py_compile` (Py 3.8 + 3.12) | Every first-party `.py` is syntactically valid. |
| `compose-validate` | `docker compose config` | All 21 `docker-compose.yml` files parse and resolve. |
| `dockerfile-lint` | [hadolint](https://github.com/hadolint/hadolint) | The custom Dockerfiles have no hard errors. |
| `shell-lint` | [shellcheck](https://www.shellcheck.net/) | Shell scripts are clean. |
| `yaml-lint` | [yamllint](https://yamllint.readthedocs.io/) | Repository-owned YAML (workflows, configs). |
| `secret-scan` | [gitleaks](https://github.com/gitleaks/gitleaks) | No *real* secrets committed. Lab demo creds are allowlisted in `.gitleaks.toml`. |
| `ci-gate` | — | Aggregates the above into one required status. |

## Run the checks locally

The same checks run via `make` (POSIX shell — Linux/macOS/WSL/Git Bash):

```bash
make install          # install ruff, yamllint, pre-commit + git hooks
make ci               # run the whole pipeline
make lint             # just ruff
make compose-validate # just docker compose config (needs Docker)
```

Prefer automatic enforcement? Install the git hooks once:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

## Conventions

- **Exploit clients** (`client.py`, `exploit.py`) are first-party Python 3 and
  are linted/compiled. Keep them passing `ruff check .`.
- **`poc.py`** files mirror upstream advisories verbatim. The Jenkins one is
  Python 2 and is excluded from linting/compilation on purpose — do not "fix" it.
- **Lab images** are pinned to vulnerable versions intentionally. Dependabot is
  configured **not** to bump them; only the GitHub Actions and the `requests`
  client dependency are tracked.
- Line endings are normalized to LF via [.gitattributes](.gitattributes).
