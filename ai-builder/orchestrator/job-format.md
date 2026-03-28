# Job Document Format

A job document is the shared contract between the Oracle (or human) and the
pipeline. It is created before the pipeline runs and read by every role.
The ARCHITECT fills in Design and Acceptance Criteria; IMPLEMENTOR and TESTER
read those sections to do their work.

---

## Job Document Structure

Based on `JOB-TEMPLATE.md`:

```markdown
# Job: <Title>

## Goal

<One paragraph describing what needs to be built and why.>

---

## Design

_To be completed by the ARCHITECT._

- Language:
- Input:
- Output:
- Edge cases to handle:
- Files to produce:
- Expected outputs for verification:

---

## Acceptance Criteria

_To be completed by the ARCHITECT._
```

**Who writes what:**

| Section | Written by | When |
|---------|-----------|------|
| Title | Oracle / human | Before pipeline runs |
| Goal | Oracle / human | Before pipeline runs |
| Design | ARCHITECT | During ARCHITECT turn |
| Acceptance Criteria | ARCHITECT | During ARCHITECT turn |

The job document is the only file that persists across all role turns within
a single pipeline run. IMPLEMENTOR and TESTER treat it as read-only after
ARCHITECT fills it in.

---

## Agent Output Format

AI agents (ARCHITECT, IMPLEMENTOR) end their response with a `<response>` XML
block the orchestrator parses. Internal agents emit plain `OUTCOME:`/`HANDOFF:`
lines.

### AI agents — XML response block

```xml
<response>
  <outcome>ARCHITECT_DESIGN_READY</outcome>
  <handoff>one paragraph summary for downstream agents</handoff>
  <documents_written>true</documents_written>
  <!-- design-mode ARCHITECT also includes: -->
  <design>## Design\n\n...</design>
  <acceptance_criteria>## Acceptance Criteria\n\n1. ...</acceptance_criteria>
  <test_command>cd /path && go test ./...</test_command>
</response>
```

The `<response>` block must be the final content of the response. XML
self-delimiting tags eliminate the JSON escaping failures that occurred with
the previous fenced-JSON format — multiline design prose, shell commands, and
code blocks are all valid inside a tag without escaping.

### Internal agents — plain lines

```
OUTCOME: HANDLER_SUBTASKS_READY
HANDOFF: decomposed into 3 components; first: store
```

### Valid outcomes per role

| Role | Valid outcomes |
|------|---------------|
| ARCHITECT | `ARCHITECT_DESIGN_READY`, `ARCHITECT_DECOMPOSITION_READY`, `ARCHITECT_NEEDS_REVISION`, `ARCHITECT_NEED_HELP` |
| IMPLEMENTOR | `IMPLEMENTOR_IMPLEMENTATION_DONE`, `IMPLEMENTOR_NEEDS_ARCHITECT`, `IMPLEMENTOR_NEED_HELP` |
| TESTER | `TESTER_TESTS_PASS`, `TESTER_TESTS_FAIL`, `TESTER_NEED_HELP` |
| DECOMPOSE_HANDLER | `HANDLER_SUBTASKS_READY`, `HANDLER_STOP_AFTER`, `HANDLER_NEED_HELP` |
| LEAF_COMPLETE_HANDLER | `HANDLER_SUBTASKS_READY`, `HANDLER_ALL_DONE`, `HANDLER_STOP_AFTER`, `HANDLER_NEED_HELP` |
| DOCUMENTER_POST_* | `DOCUMENTER_DONE` |

Any outcome ending in `_NEED_HELP` halts the pipeline and signals that human
intervention is required. The orchestrator exits with code 0.

### HANDOFF accumulation

The `handoff` field (XML for AI agents; `HANDOFF:` line for internal agents)
is appended to `handoff_history` after every invocation and injected into
every subsequent AI agent's prompt as `## Handoff Notes from Previous Agents`.
Internal agents are excluded from receiving history (`no_history: true` in the
machine JSON).

---

## Job Document Lifecycle (TM mode)

In TM mode, the job document is a task `README.md` in the target repository's
task tree. The orchestrator reads it for supplementary context; the primary
inputs to each agent come from `task.json` fields injected inline into the
prompt. Agents do not edit the job document.

```
Oracle creates task README + task.json (goal, context, complexity)
    |
    v
orchestrator reads task.json → injects goal/context/complexity inline
    |
    v
ARCHITECT emits XML <response> → orchestrator stores design fields in task.json
    |
    v
orchestrator injects design/acceptance_criteria/test_command inline
    |
    v
IMPLEMENTOR writes source files to output_dir
    |
    v
TESTER reads test_command from task.json, runs subprocess
    |
    v
LEAF_COMPLETE_HANDLER advances current-job.txt to next sibling
    |
    v
Pipeline completes → orchestrator writes metrics, renders README,
rebuilds master-index.md, applies deferred TOP rename
```

`current-job.txt` (in `--run-dir`) always points to the active job document.
It is updated by `set-current-job.sh` (DECOMPOSE_HANDLER after creating
subtasks) and by `on-task-complete.sh` (LEAF_COMPLETE_HANDLER after completion).
