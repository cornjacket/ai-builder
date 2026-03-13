# Routing

The orchestrator routes between roles using a lookup table keyed on
`(current_role, outcome)`. Each entry maps to either the next role name
or `None` (halt).

---

## ROUTES Table

### TM Mode

| From | Outcome | To |
|------|---------|----|
| ARCHITECT | `DONE` | [DOCUMENTER hook] → IMPLEMENTOR |
| ARCHITECT | `NEED_HELP` | halt |
| IMPLEMENTOR | `DONE` | [DOCUMENTER hook] → TESTER |
| IMPLEMENTOR | `NEEDS_ARCHITECT` | ARCHITECT |
| IMPLEMENTOR | `NEED_HELP` | halt |
| TESTER | `DONE` | [DOCUMENTER hook] → TASK_MANAGER |
| TESTER | `FAILED` | IMPLEMENTOR |
| TESTER | `NEED_HELP` | halt |
| TASK_MANAGER | `DONE` | halt (Oracle decides next run) |
| TASK_MANAGER | `NEED_HELP` | halt |

### Non-TM Mode

| From | Outcome | To |
|------|---------|----|
| ARCHITECT | `DONE` | IMPLEMENTOR |
| ARCHITECT | `NEED_HELP` | halt |
| IMPLEMENTOR | `DONE` | TESTER |
| IMPLEMENTOR | `NEEDS_ARCHITECT` | ARCHITECT |
| IMPLEMENTOR | `NEED_HELP` | halt |
| TESTER | `DONE` | halt (pipeline complete) |
| TESTER | `FAILED` | IMPLEMENTOR |
| TESTER | `NEED_HELP` | halt |

DOCUMENTER hook does not run in non-TM mode.

---

## NEED_HELP Handling

`NEED_HELP` from any role is handled before the ROUTES lookup. The
orchestrator prints a message, optionally prints the job document path, and
exits with code 0. It is not an error — it signals that human intervention
is required and the pipeline is paused, not failed.

---

## Unrecognised Outcomes

If an outcome is not present in the ROUTES table and is not `NEED_HELP`, the
orchestrator halts with exit code 1 and logs the unrecognised value. This
catches cases where an agent emits a malformed or unexpected OUTCOME string.

---

## DOCUMENTER Hook

In TM mode, the orchestrator inserts a DOCUMENTER post-step between certain
roles and their routing destination. DOCUMENTER is not a node in the ROUTES
table — it is managed directly by the orchestrator loop.

**Trigger config:**
```python
DOCUMENTER_TRIGGERS = {"ARCHITECT", "IMPLEMENTOR", "TESTER"}
```

TASK_MANAGER is excluded — it updates task metadata only and produces no
documentation artifacts.

**Hook logic:**
```
1. Role completes → outcome and DOCS field parsed
2. next_role = ROUTES[(current_role, outcome)]   ← saved as pending
3. if current_role in DOCUMENTER_TRIGGERS and DOCS is non-empty:
       run DOCUMENTER with context:
         - which role just ran
         - job document path
         - output directory
         - HANDOFF text from triggering role
         - DOCS instructions from triggering role
4. route to pending next_role
```

DOCUMENTER receives the `DOCS:` field written by the triggering role.
The content producer — not DOCUMENTER — decides what documentation is needed
and provides instructions. DOCUMENTER executes those instructions.

If `DOCS:` is absent or `none`, step 3 is skipped entirely.

---

## Agent Assignment

```python
AGENTS = {
    "TASK_MANAGER": "claude",
    "ARCHITECT":    "claude",
    "IMPLEMENTOR":  "gemini",
    "TESTER":       "claude",
}
```

Agent assignment is a static configuration. The orchestrator looks up the
agent name for the current role and passes it to `agent_wrapper.run_agent()`.
