# Task: design-model-role-addendum-in-machine-config

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | orchestrator, machine-config, design               |
| Priority    | MED           |
| Category    | gemini-compat          |
| Next-subtask-id | 0000               |

## Goal

Review and decide whether agent-specific role prompt addenda (currently
hardcoded in `gemini_compat.py`) should instead be declared in the machine
JSON, making them configuration rather than code.

## Context

The current implementation in `gemini_compat.py` hard-codes Gemini-specific
prompt additions per role:

```python
# gemini_compat.py
def gemini_role_addendum(role: str) -> str:
    if role == "IMPLEMENTOR":
        # heredoc prohibition rule
        ...
```

`build_prompt()` in `orchestrator.py` calls this when `agent == "gemini"`.

An alternative is to declare the addendum in the machine JSON alongside the
role's existing `"prompt"` field:

```json
"IMPLEMENTOR": {
  "agent": "gemini",
  "prompt": "roles/IMPLEMENTOR.md",
  "prompt_addendum": "roles/addenda/IMPLEMENTOR-gemini.md"
}
```

The orchestrator would read and append `prompt_addendum` when building the
prompt, and `gemini_compat.py` would no longer be needed.

### Arguments for machine config

- Consistent with the existing `"prompt"` field — all prompt configuration
  lives in one place.
- Different machine files could use different addenda (e.g. a Gemini machine
  with a stricter IMPLEMENTOR addendum vs a permissive one for testing).
- No Python code change needed when a new rule is added — just edit a
  Markdown file and update the machine JSON.

### Arguments for keeping it in `gemini_compat.py`

- The addenda are agent-capability workarounds, not pipeline configuration.
  They apply to all Gemini machines equally and should not need per-machine
  variation.
- A `prompt_addendum` field in the machine JSON adds schema complexity and
  a new orchestrator code path for what may be a small and stable set of rules.
- `gemini_compat.py` is already isolated and well-commented — it is easy to
  find and update.
- If a future agent (e.g. a third CLI) also needs addenda, `gemini_compat.py`
  generalises naturally to an `agent_compat.py` pattern.

### Decision criteria

- How many Gemini-specific addenda do we anticipate accumulating?
- Do we expect addenda to vary between machine files, or always apply uniformly?
- Is the `prompt_addendum` field worth the schema and orchestrator complexity?

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
