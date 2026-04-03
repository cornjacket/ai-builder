# Task: github-actions-ci-workflow

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | f00df6-unit-smoke-test-script             |
| Priority    | —           |
| Created     | 2026-04-02            |
| Completed | 2026-04-02 |
| Next-subtask-id | 0000               |

## Goal

Create `.github/workflows/unit-tests.yml` — GitHub Actions CI workflow
that runs the unit smoke test on every push and PR to main.

## Context

No CI exists today. This workflow is the cloud-side counterpart to the local
`run-unit-tests.sh` script — it calls the same script so local and CI
behaviour are identical.

Workflow spec:
- Triggers: `pull_request` targeting `main` (pre-merge check) and `push` to
  `main` (post-merge confirmation — fires when PR is merged via web UI)
- Runner: `ubuntu-latest`
- Steps: checkout → set up Python 3.11 → pip install requirements-dev.txt →
  install bats-core → run `bash tests/unit/run-unit-tests.sh --coverage`
- Upload coverage report as artifact on every run (`if: always()`)
- Job name: `unit-tests`

Prerequisite: subtask 0004 (sed portability fix) complete.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
