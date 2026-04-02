# machines/doc/

State machine and role prompts for the **doc pipeline** — a documentation
generation pipeline that traverses an existing source tree and writes
structured `.md` files alongside each source file.

---

## Files

| File / Directory | Purpose |
|------------------|---------|
| `default.json` | Doc pipeline state machine — roles, transitions, route_on config |
| `roles/` | Role prompt files for the doc pipeline agents |
| `roles/DOC_ARCHITECT.md` | Prompt for DOC_ARCHITECT (decompose and atomic modes) |
| `roles/DOC_INTEGRATOR.md` | Prompt for DOC_INTEGRATOR (integrate nodes only) |

---

## Pipeline Overview

The doc pipeline reuses the same recursive task tree infrastructure as the
builder pipeline but drives documentation agents instead of implementation
agents.

**Roles:**

| Role | Agent | Responsibility |
|------|-------|----------------|
| DOC_ARCHITECT | claude | Decompose mode: scan directory, identify sub-components, return components JSON (no docs written). Atomic mode: read source files, write companion `.md` and `README.md`. |
| DECOMPOSE_HANDLER | internal | Creates pipeline subtask directories from DOC_ARCHITECT's components array; writes `component_type: integrate` to the integrate subtask's `task.json`. |
| POST_DOC_HANDLER | internal | Markdown linter — checks Purpose/Tags headers, empty sections, placeholder text. Emits typed pass/fail outcomes. |
| LEAF_COMPLETE_HANDLER | internal | Runs `on-task-complete.sh`; uses `route_on` to emit `HANDLER_INTEGRATE_READY` for integrate subtasks, `HANDLER_SUBTASKS_READY` for all others. |
| DOC_INTEGRATOR | claude | Runs only at integrate nodes; reads handoff summaries from sub-components and writes cross-component synthesis docs (`README.md`, `data-flow.md`, `api.md`). |

**Flow at an atomic leaf:**
```
DOC_ARCHITECT (atomic) → POST_DOC_HANDLER → LEAF_COMPLETE_HANDLER → (next sibling or up)
```

**Flow at a composite node:**
```
DOC_ARCHITECT (decompose) → DECOMPOSE_HANDLER → [recurse into children]
    → LEAF_COMPLETE_HANDLER (integrate ready) → DOC_INTEGRATOR
    → POST_DOC_HANDLER → LEAF_COMPLETE_HANDLER → (next sibling or up)
```

---

## route_on config

`LEAF_COMPLETE_HANDLER` is configured with `route_on` so it can distinguish
between a normal next-sibling advance and a transition to the integrate step:

```json
"route_on": {
    "field":     "component_type",
    "default":   "HANDLER_SUBTASKS_READY",
    "integrate": "HANDLER_INTEGRATE_READY"
}
```

`DECOMPOSE_HANDLER` writes `"component_type": "integrate"` to the integrate
subtask's `task.json` at creation time. When LCH reaches that subtask as the
next task, it reads this field and emits `HANDLER_INTEGRATE_READY` instead of
`HANDLER_SUBTASKS_READY`, routing directly to `DOC_INTEGRATOR`.

---

## Usage

```bash
python3 ai-builder/orchestrator/orchestrator.py \
    --job         "$README" \
    --target-repo <target-repo> \
    --output-dir  <output-dir> \
    --epic        main \
    --state-machine ai-builder/orchestrator/machines/doc/default.json
```

See the regression test at `tests/regression/doc-user-service/` for a
complete working example with reset and run scripts.
