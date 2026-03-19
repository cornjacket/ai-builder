# Task: audit-and-schema-design

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 829461-split-task-format-md-json-and-scripts             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Enumerate every field used by every script, template, and role in the task
system. Define the exact schema for `task.json` (pipeline subtasks) and the
cleaned-up README format for user tasks. Produce the migration contract that
all subsequent subtasks implement against.

## Context

See parent task `829461-split-task-format-md-json-and-scripts` for motivation.

## Notes

### Field Audit

#### Fields across all task types

| Field | USER-TASK | USER-SUBTASK | PIPELINE-SUBTASK | Read by | Written by |
|-------|-----------|--------------|------------------|---------|------------|
| Task-type | USER-TASK | USER-SUBTASK | PIPELINE-SUBTASK | `advance-pipeline.sh` (boundary detection), orchestrator (entry-point validation) | creation scripts (template) |
| Status | complete | ✓ | ✓ | `complete-task.sh`, `move-task.sh`, `list-tasks.sh` | `complete-task.sh`, `move-task.sh`, `wont-do-subtask.sh` |
| Epic | ✓ | ✓ | ✓ | `list-tasks.sh` | creation scripts (template) |
| Tags | ✓ | ✓ | ✓ | `list-tasks.sh` (--tag filter) | creation scripts (template) |
| Parent | — | ✓ | ✓ | (informational only) | creation scripts (template) |
| Priority | ✓ | ✓ | ✓ | `list-tasks.sh` (--sort-priority) | creation scripts (template) |
| Next-subtask-id | ✓ | ✓ | ✓ | `task-id-helpers.sh` | `task-id-helpers.sh` (auto-increment) |
| Complexity | — | — | ✓ | orchestrator (routes ARCHITECT mode: atomic vs composite) | creation scripts (template, default —) |
| Level | — | — | ✓ | orchestrator (entry-point validation, live log walk-up) | `new-pipeline-build.sh` (TOP), `new-pipeline-subtask.sh` (INTERNAL) |
| Last-task | — | — | ✓ | `advance-pipeline.sh`, `is-last-task.sh` | DECOMPOSE_HANDLER (sets true on last subtask) |
| Stop-after | — | — | ✓ | `check-stop-after.sh` (called by `on-task-complete.sh`) | agents (set to true to pause) |
| Subtasks list | ✓ | ✓ | ✓ | `next-subtask.sh`, `subtasks-complete.sh` | all subtask creation/completion scripts |
| Components table | — | — | ✓ (composite) | orchestrator (DECOMPOSE_HANDLER prompt) | ARCHITECT (agent) |

**Key observation:** `Complexity`, `Level`, `Last-task`, `Stop-after`, and `Components`
are pipeline-only. User tasks and user subtasks carry them unnecessarily today.

**Key observation:** Tags, Parent, Epic are read only for filtering/display — never
used for pipeline execution logic.

---

### Proposed Schema

#### Pipeline subtask: `task.json`

All structured metadata moves here. Scripts and orchestrator read/write only this file.

```json
{
  "task-type": "PIPELINE-SUBTASK",
  "status": "—",
  "epic": "main",
  "parent": "<parent-rel-path>",
  "priority": "—",
  "next-subtask-id": "0000",
  "complexity": "—",
  "level": "INTERNAL",
  "last-task": false,
  "stop-after": false,
  "components": [
    {
      "name": "<component-name>",
      "complexity": "atomic|composite",
      "description": "<full contract>"
    }
  ],
  "subtasks": [
    { "name": "<subtask-dir-name>", "complete": false }
  ]
}
```

**Notes:**
- `components` is empty array `[]` until ARCHITECT fills it (Design Mode: stays empty; Decompose Mode: ARCHITECT writes it)
- `subtasks` replaces the `<!-- subtask-list-start/end -->` markers in README
- `stop-after` and `last-task` are booleans (not strings)
- `complexity` values: `"—"` (unset/top-level), `"atomic"`, `"composite"`
- `level` values: `"TOP"`, `"INTERNAL"`

#### Pipeline subtask: `README.md`

Prose only. No metadata table. AI agents read and write these sections.

```markdown
# Task: <name>

## Goal
## Context
## Components
## Design
## Acceptance Criteria
## Test Command
## Suggested Tools
## Notes
```

`## Components` stays in README as prose — ARCHITECT writes a paragraph describing
data flow plus the table. The structured array goes in `task.json`; the human-readable
prose stays in README. DECOMPOSE_HANDLER (internal) reads the array from `task.json`;
ARCHITECT (claude) reads the prose from README.

#### User task / user subtask: `README.md` only

No `task.json`. Metadata stays in the README header table, stripped of pipeline-only fields.

```markdown
# Task: <name>

| Field           | Value        |
|-----------------|--------------|
| Task-type       | USER-TASK    |
| Status | complete |
| Epic            | main         |
| Tags            | —            |
| Priority        | HIGH         |
| Next-subtask-id | 0000         |

## Goal
## Context
## Subtasks
## Notes
```

User subtasks: same but with `Task-type: USER-SUBTASK` and a `Parent` field. No
`Complexity`, `Level`, `Last-task`, `Stop-after`.

---

### Script Responsibilities After Split

| Script | Reads | Writes |
|--------|-------|--------|
| `new-pipeline-subtask.sh` | parent `task.json` (Next-subtask-id) | child `task.json` + child `README.md` |
| `new-pipeline-build.sh` | parent `task.json` (Next-subtask-id) | child `task.json` + child `README.md` |
| `complete-task.sh` (pipeline) | `task.json` (Status) | `task.json` (Status → complete) |
| `advance-pipeline.sh` | `task.json` (Last-task, Task-type, Level) | `task.json` (Status) |
| `check-stop-after.sh` | `task.json` (stop-after) | — |
| `is-last-task.sh` | `task.json` (last-task) | — |
| `is-top-level.sh` | `task.json` (level) | — |
| `next-subtask.sh` | `task.json` (subtasks array) | — |
| `subtasks-complete.sh` | `task.json` (subtasks array) | — |
| `on-task-complete.sh` | `task.json` (stop-after, last-task) via child scripts | `task.json` (status, subtask entry) |
| `new-user-task.sh` | — | `README.md` only |
| `new-user-subtask.sh` | parent `README.md` (Next-subtask-id, subtasks list) | child `README.md`, parent `README.md` |
| `complete-task.sh` (user) | `README.md` (Status) | `README.md` (Status, subtasks list) |
| `move-task.sh` | `README.md` (Status) | `README.md` (Status) |
| `list-tasks.sh` | `README.md` (Tags, Priority) OR `task.json` (pipeline) | — |

**Note:** `list-tasks.sh` needs to handle both formats since it lists both user tasks
and pipeline subtasks.

---

### Orchestrator Changes

The orchestrator currently reads these fields from README via regex:
- `Task-type` — validate entry point is PIPELINE-SUBTASK
- `Level` — validate entry point is TOP; walk-up for live log
- `Complexity` — route ARCHITECT to Design vs Decompose Mode

After the split, all three are read from `task.json` via `json.load()`. Cleaner,
faster, no regex.

DECOMPOSE_HANDLER (internal) reads `components` array from `task.json` and:
1. Creates subtask directories (calling `new-pipeline-subtask.sh`)
2. Sets Last-task and Level on the final subtask's `task.json`
3. Writes Goal and Context into each subtask's `README.md`
4. Calls `set-current-job.sh` to point at the first subtask

---

### Migration Plan

Existing tasks in `project/tasks/` are user tasks and user subtasks — they keep
README-only format (just stripped of pipeline-only fields, which they currently
have but shouldn't). No `task.json` needed for existing tasks.

New pipeline subtasks created by `new-pipeline-build.sh` and `new-pipeline-subtask.sh`
(after this change) will produce `task.json` + `README.md`. The regression target
repos are always freshly created by `reset.sh`, so no migration of existing pipeline
tasks is needed.

The `task-template.md` (legacy, appears unused by current scripts) can be deleted.
