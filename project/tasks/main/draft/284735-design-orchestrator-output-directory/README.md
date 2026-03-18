# Task: design-orchestrator-output-directory

| Field    | Value                |
|----------|----------------------|
| Status   | draft           |
| Epic     | main             |
| Tags     | orchestrator, design             |
| Parent   | —           |
| Priority | MED         |
| Next-subtask-id | 0000               |
## Description

Design the long-term home for orchestrator output: job documents, execution
logs, agent logs, and generated artifacts.

Currently `--output-dir` is caller-specified and ephemeral. Job documents
created by the TASK MANAGER are written there temporarily. This works for
now but raises questions about where this output should live permanently.

**Questions to resolve:**

- Should job documents be discarded after a pipeline run, or preserved?
- If preserved, should they live under a directory tree similar to
  `project/tasks/` — e.g. `orchestrator/runs/<date>-<id>/` — so pipeline
  history is inspectable?
- Should the output directory be caller-specified (`--output-dir`) or should
  the orchestrator own it (e.g. always writing to `orchestrator/` in the
  target repo)?
- Is there value in a structured run index (like an execution manifest) so
  past runs can be replayed or audited?
- How do generated application artifacts (code, configs) relate to run
  history — should they stay in `output-dir` or be moved to the target repo
  after a successful TESTER pass?

**Current behaviour (interim):**
Job documents are written to `output_dir/` alongside `execution.log` and
agent logs. The directory is caller-specified. No structured retention policy.

## Documentation

Decisions made here should be documented in `ai-builder/FLOW.md` and
reflected in `orchestrator.py` and `target/SETUP.md`.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

The `project/tasks/` tree is the model to consider for inspiration: each run
could be a directory with a README summarising what was built, containing the
job doc, execution log, and a pointer to the generated artifacts.
