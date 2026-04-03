# CI: Unit Tests

**Workflow file:** `.github/workflows/unit-tests.yml`
**Job name:** `unit-tests`
**Runner:** `ubuntu-latest`

## What it does

Runs the full unit test suite (`tests/unit/run-unit-tests.sh --coverage`) on
every PR targeting `main` and every push to `main`. Uploads a `.coverage`
artifact on every run.

## Triggers

| Event | Condition |
|---|---|
| `pull_request` | Targeting `main`, paths below changed |
| `push` | To `main`, paths below changed |

**Path filters** — the workflow only runs when these paths are touched:

```
tests/unit/**
ai-builder/orchestrator/**
project/tasks/scripts/**
bootstrap/**
requirements-dev.txt
.github/workflows/unit-tests.yml
```

Changes to docs, task tracking files, and CLAUDE.md do not trigger a run.

## Test suites

| Suite | Runner | Command |
|---|---|---|
| Python | pytest | `pytest tests/unit/ --cov=ai-builder/orchestrator` |
| Shell | bats | `bats tests/unit/shell/` |

See `tests/unit/run-unit-tests.sh` for the full runner script.

## Running locally

```bash
# Full suite
bash tests/unit/run-unit-tests.sh

# Python only
bash tests/unit/run-unit-tests.sh --python

# Shell only
bash tests/unit/run-unit-tests.sh --shell

# With coverage report
bash tests/unit/run-unit-tests.sh --coverage
```

Requires `pytest` and `pytest-cov` (`pip install -r requirements-dev.txt`) and
`bats-core` (`brew install bats-core` on macOS, `apt-get install bats` on Linux).

## Branch protection

Once this workflow has run at least once, add `unit-tests` as a required status
check in the GitHub branch protection ruleset for `main`. See task
`69f69b-github-branch-protection-setup` for setup steps.
