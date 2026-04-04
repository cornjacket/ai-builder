# Task: adopt-mypy-static-type-checking

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | —                      |
| Next-subtask-id | 0000               |

## Goal

Decide whether to adopt mypy as a static type checker for the orchestrator
codebase and, if so, configure it and integrate it into the local dev workflow.

## Context

The codebase uses type annotations (`Path`, `dataclass`, `Protocol`, etc.) but
has no mypy configuration. The immediate trigger was the `InternalAgent`
Protocol introduced in task
[`356c4e-extract-internal-agents-into-configurable-modules`](../356c4e-extract-internal-agents-into-configurable-modules/):
mypy would statically verify that every agent class satisfies the Protocol's
method signature, which `@runtime_checkable` + `isinstance` cannot do (it only
checks method existence, not signatures).

Decision factors:
- Does the annotation coverage across `orchestrator.py` and the new `agents/`
  package make mypy useful enough to justify the setup cost?
- What strictness level (`--strict`, `--ignore-missing-imports`, etc.) is
  appropriate given the current annotation density?
- Should mypy run as a pre-commit hook, a `make` target, or both?
- Are there third-party packages (subprocess, pathlib, dataclasses) that need
  stub packages?

If adopted, this task also covers adding a `mypy.ini` or `[tool.mypy]` section
to `pyproject.toml`, fixing any errors surfaced on the first run, and
documenting the workflow in the orchestrator README.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
