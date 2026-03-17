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

Every agent ends its response with a structured block the orchestrator parses:

```
OUTCOME: <value>
HANDOFF: <one paragraph summary for the next agent>
DOCS: <documentation instructions for the DOCUMENTER, or 'none'>
```

### OUTCOME

Valid outcomes per role:

| Role | Valid outcomes |
|------|---------------|
| ARCHITECT | `DONE`, `NEED_HELP` |
| IMPLEMENTOR | `DONE`, `NEEDS_ARCHITECT`, `NEED_HELP` |
| TESTER | `DONE`, `FAILED`, `NEED_HELP` |
| DECOMPOSE_HANDLER     | `HANDLER_SUBTASKS_READY`, `HANDLER_NEED_HELP` |
| LEAF_COMPLETE_HANDLER | `HANDLER_SUBTASKS_READY`, `HANDLER_ALL_DONE`, `HANDLER_STOP_AFTER`, `HANDLER_NEED_HELP` |

`NEED_HELP` from any role halts the pipeline and signals that human
intervention is required. The orchestrator exits with code 0.

### HANDOFF

A one-paragraph summary of what was done and what the next agent needs to
know. Accumulated across all roles and injected into every subsequent
agent's prompt as `## Handoff Notes from Previous Agents`.

### DOCS

Instructions for the DOCUMENTER hook. Written by the role that produced the
content — the content producer is the authority on what needs documenting.

Format: free prose describing what files to create or update and what
sections to include. Example:

```
DOCS: Create leaf README at fibonacci/README.md. Sections needed:
  - Purpose: computes first N Fibonacci numbers
  - Interface: Compute(n int) []int — returns empty slice for n<=0
  - Usage example from the test cases
```

If the role produced no documentation-worthy output, omit `DOCS:` or write
`DOCS: none`. The DOCUMENTER hook is skipped for that step.

---

## Job Document Lifecycle

```
Oracle creates job doc from JOB-TEMPLATE.md
    |
    v
ARCHITECT fills in Design + Acceptance Criteria (edits the file in place)
    |
    v
IMPLEMENTOR reads Design, produces implementation files in output-dir
    |
    v
TESTER reads Acceptance Criteria, verifies implementation
    |
    v
Pipeline halts; job doc remains in output-dir as a record of the run
```

In TM mode, the job document path is written to `current-job.txt` in the
output directory by LEAF_COMPLETE_HANDLER, then read by the orchestrator to pass to
downstream roles.
