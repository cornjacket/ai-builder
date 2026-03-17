# machines/

State machine definition files for the ai-builder orchestrator.

Each file is a JSON document that fully describes one pipeline configuration:
entry point, role→agent mapping, prompt files, and the full transition table.

---

## Files

| File | Purpose |
|------|---------|
| `default.json` | Full pipeline with TM handlers. Used when `--target-repo` is provided and no `--state-machine` is specified. |
| `simple.json` | Flat (non-TM) pipeline. Used when only `--job` is provided and no `--state-machine` is specified. |

---

## Format

```json
{
  "start_state": "ARCHITECT",
  "roles": {
    "<ROLE>": { "agent": "<cli-name>", "prompt": "<path-relative-to-repo-root-or-null>" }
  },
  "transitions": {
    "<ROLE>": {
      "<OUTCOME>": "<NEXT_ROLE or null>"
    }
  }
}
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `start_state` | yes | Default entry role. Overridable with `--start-state`. |
| `roles` | yes | Per-role configuration. Every role referenced in `transitions` must appear here. |
| `roles[R].agent` | yes | Agent CLI name to invoke for this role (`claude`, `gemini`, etc.). |
| `roles[R].prompt` | yes | Path to the role's static prompt file (relative to repo root), or `null` for dynamic generation. |
| `transitions` | yes | State diagram. Each key is a role; each value maps outcome strings to next roles (`null` = halt). |

### `prompt: null`

Roles with `"prompt": null` use the orchestrator's built-in prompt generation
(currently `DECOMPOSE_HANDLER` and `LEAF_COMPLETE_HANDLER`, which require
runtime variable injection). Once a template variable injection system is
implemented (task `7eec4a`), these can be extracted to static prompt files.

---

## Custom Machine Files

Pass any conforming JSON file with `--state-machine <file>` to use a custom
pipeline configuration. The orchestrator validates the file at startup:

- All roles referenced in `transitions` must appear in `roles`.
- All next-role values (non-null) must appear in `roles`.
- `start_state` must appear in `roles`.

Custom machine files enable testing sub-pipelines, alternate role orderings,
or pipelines with different agent assignments without modifying the source.
