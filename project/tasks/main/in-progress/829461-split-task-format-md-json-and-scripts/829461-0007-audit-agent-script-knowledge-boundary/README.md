# Task: audit-agent-script-knowledge-boundary

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 829461-split-task-format-md-json-and-scripts             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Audit `CLAUDE.md` and all agent role prompts to confirm that AI agents have
no knowledge of task management scripts beyond what they strictly need.
Document the knowledge boundary as a formal rule in `CLAUDE.md` and the
relevant role docs.

## Context

AI agents (ARCHITECT, IMPLEMENTOR, TESTER) should only know about:
- The job document (`README.md`) — they read and write it
- Target-repo build/test commands (e.g. `go test ./...`) — from `## Suggested Tools`

They should have zero knowledge of:
- Task management scripts (`new-pipeline-subtask.sh`, `complete-task.sh`, etc.)
- `task.json` — structure, fields, location
- `current-job.txt` — how the pipeline advances
- Any orchestrator internals

The only agent that previously needed script knowledge was DECOMPOSE_HANDLER,
and that role is being made internal (no AI prompt). LEAF_COMPLETE_HANDLER
is already internal.

Currently `CLAUDE.md` documents the full task management system including all
scripts and their usage. This is appropriate for the human/Oracle operator but
must not leak into agent prompts. The audit should verify:

1. No role prompt (`roles/*.md`) references task scripts or `task.json`
2. `CLAUDE.md` does not get injected into agent prompts (confirmed via `cwd=/tmp`)
3. The boundary is explicitly documented: agents own `README.md` prose;
   the orchestrator and scripts own everything else

If any role prompt contains script references, remove them. Add a section to
`CLAUDE.md` and/or `ai-builder/orchestrator/README.md` documenting this
boundary formally so it is not accidentally violated in future prompt edits.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
