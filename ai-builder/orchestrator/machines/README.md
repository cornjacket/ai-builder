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
| `default-gemini.json` | Same as `default.json` but with all AI roles set to `"agent": "gemini"`. |
| `simple-gemini.json` | Same as `simple.json` but with all AI roles set to `"agent": "gemini"`. |

---

## Format

```json
{
  "start_state": "ARCHITECT",
  "roles": {
    "<ROLE>": {
      "agent": "<cli-name>",
      "prompt": "<path-relative-to-repo-root-or-null>",
      "no_history": false
    }
  },
  "transitions": {
    "<ROLE>": {
      "<OUTCOME>": "<NEXT_ROLE or null>"
    }
  }
}
```

### Fields

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `start_state` | yes | — | Default entry role. Overridable with `--start-state`. |
| `roles` | yes | — | Per-role configuration. Every role referenced in `transitions` must appear here. |
| `roles[R].agent` | yes | — | Agent CLI name to invoke for this role (`claude`, `gemini`, etc.). |
| `roles[R].prompt` | yes | — | Path to the role's static prompt file (relative to repo root), or `null` for dynamic generation. |
| `roles[R].no_history` | no | `false` | If `true`, the role receives no accumulated handoff history in its prompt — only its role instructions and the current job doc. See [Handoff History Policy](#handoff-history-policy) below. |
| `transitions` | yes | — | State diagram. Each key is a role; each value maps outcome strings to next roles (`null` = halt). |

### `prompt: null`

Roles with `"prompt": null` use the orchestrator's built-in prompt generation
(currently `DECOMPOSE_HANDLER` and `LEAF_COMPLETE_HANDLER`, which require
runtime variable injection). Once a template variable injection system is
implemented (task `7eec4a`), these can be extracted to static prompt files.

### Handoff History Policy

The orchestrator maintains a running list of agent handoffs. By default every
role receives this history as context. Setting `"no_history": true` strips the
history section from that role's prompt entirely — the role sees only its own
instructions and the current job document.

**When to use `no_history: true`:**
- The role's work is self-contained and does not depend on prior agent decisions
  (e.g. a handler that just runs a shell script, or a tester that only needs
  the acceptance criteria from the job doc)
- You want to reduce token usage for roles that would otherwise accumulate large
  amounts of irrelevant context

**When to keep `no_history: false`:**
- The role needs to understand decisions made by earlier agents in the same
  decomposition frame (e.g. ARCHITECT needs the decomposition rationale,
  IMPLEMENTOR needs the design ARCHITECT produced)

**`default.json` policy:**

| Role | `no_history` | Rationale |
|------|-------------|-----------|
| ARCHITECT | `false` | Needs full design lineage to make informed decisions |
| IMPLEMENTOR | `false` | Needs ARCHITECT's design from the current frame |
| TESTER | `true` | Only needs the job doc (acceptance criteria) to run tests |
| DECOMPOSE_HANDLER | `true` | Runs a fixed script sequence; prior context unused |
| LEAF_COMPLETE_HANDLER | `true` | Runs one script and maps output to an outcome string |

---

## Custom Machine Files

Pass any conforming JSON file with `--state-machine <file>` to use a custom
pipeline configuration. The orchestrator validates the file at startup:

- All roles referenced in `transitions` must appear in `roles`.
- All next-role values (non-null) must appear in `roles`.
- `start_state` must appear in `roles`.

Custom machine files enable testing sub-pipelines, alternate role orderings,
or pipelines with different agent assignments without modifying the source.
