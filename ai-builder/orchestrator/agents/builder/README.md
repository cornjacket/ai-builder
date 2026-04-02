# agents/builder/

Builder-specific internal agent implementations. These classes handle the
pipeline roles defined in the builder machine configurations
(`machines/builder/`).

---

## Files

| File | Description |
|------|-------------|
| `tester.py` | `TesterAgent` — runs `test_command` from `task.json` |
| `documenter.py` | `DocumenterAgent` — scans output dir for `.md` files; rebuilds README documentation index |
| `decompose.py` | `DecomposeAgent` — creates pipeline subtask directories from ARCHITECT's components list |
| `lch.py` | `LCHAgent` — runs `on-task-complete.sh`; maps output tokens to pipeline outcomes |

---

## Context requirements

| Agent | Requires `AgentContext`? |
|-------|--------------------------|
| `TesterAgent` | No |
| `DocumenterAgent` | No |
| `DecomposeAgent` | Yes |
| `LCHAgent` | Yes |

Context-free agents take no constructor arguments.
Context-aware agents receive `ctx: AgentContext` at construction time.
See [`../context.py`](../context.md) for `AgentContext` field definitions.

---

## Machine JSON configuration

```json
"TESTER":                     { "agent": "internal", "impl": "agents.builder.tester.TesterAgent",        "prompt": null },
"DECOMPOSE_HANDLER":          { "agent": "internal", "impl": "agents.builder.decompose.DecomposeAgent",  "prompt": null },
"LEAF_COMPLETE_HANDLER":      { "agent": "internal", "impl": "agents.builder.lch.LCHAgent",              "prompt": null },
"DOCUMENTER_POST_ARCHITECT":  { "agent": "internal", "impl": "agents.builder.documenter.DocumenterAgent","prompt": null },
"DOCUMENTER_POST_IMPLEMENTOR":{ "agent": "internal", "impl": "agents.builder.documenter.DocumenterAgent","prompt": null }
```

`LCHAgent` also accepts an optional `route_on` object (see
[`lch.md`](lch.md)) that enables different outcome tokens for different
next-task types. The builder pipeline does not use this; the doc pipeline does.
