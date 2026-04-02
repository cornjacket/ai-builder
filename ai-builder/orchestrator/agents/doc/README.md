# agents/doc/

Doc-pipeline internal agent implementations. These classes handle the internal
roles defined in `machines/doc/default.json`.

---

## Files

| File | Description |
|------|-------------|
| `linter.py` | `MarkdownLinterAgent` — lints `.md` files written in the current step; emits typed pass/fail outcomes |

---

## Context requirements

| Agent | Requires `AgentContext`? |
|-------|--------------------------|
| `MarkdownLinterAgent` | No |

Context-free agents take no constructor arguments.

---

## Machine JSON configuration

```json
"POST_DOC_HANDLER": { "agent": "internal", "impl": "agents.doc.linter.MarkdownLinterAgent", "prompt": null }
```
