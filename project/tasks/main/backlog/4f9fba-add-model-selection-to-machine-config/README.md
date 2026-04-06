# Task: add-model-selection-to-machine-config

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | HIGH        |
| Category    | gemini-compat          |
| Next-subtask-id | 0000               |

## Goal

Add a **required** `"model"` field to the machine JSON role config so that each
role explicitly pins the model to use. Machine files without a `"model"` field
on every AI role are rejected at load time.

**Design constraint: model versions must be pinned.**
Every pipeline invocation must use exactly the model specified in the machine
file. Implicit defaults (CLI defaults that change as providers update) and
auto-routing (Gemini's `auto-gemini-3` per-turn router) are both disallowed in
machine files — they introduce variability across invocations, making regression
comparisons and debugging unreliable. Auto-routing is only permitted via CLI
override for manual experimentation.

**Reference:** [`learning/agent-model-selection.md`](../../../../../learning/agent-model-selection.md)

## Context

Both Claude and Gemini CLIs support `--model <id>`. Currently the pipeline
passes no `--model` flag to either, so both use their CLI defaults
(Claude: `claude-sonnet-4-6`; Gemini: `auto-gemini-3` per-turn router).

If the `"model"` field were optional, runs would default to whatever the CLI's
current default is — which changes as providers update. Two runs of the same
machine file against the same input could silently use different models, making
regressions unreliable and cost comparisons meaningless.

Per-role model pinning enables:
- Reproducible runs: same machine file always invokes the same models
- Cost control: expensive roles (ARCHITECT) pinned to capable models; cheap roles (TESTER) to efficient models
- Mixing agents and models across roles in a single pipeline run

**Machine JSON change:**

```json
"roles": {
  "ARCHITECT":   { "agent": "claude",  "model": "claude-opus-4-6",       ... },
  "IMPLEMENTOR": { "agent": "gemini",  "model": "gemini-3-flash-preview", ... },
  "TESTER":      { "agent": "claude",  "model": "claude-haiku-4-5",       ... }
}
```

`auto-gemini-3` is **not a valid value** in machine files. The schema validator
must reject it with a clear error message directing the user to pin a specific
model ID.

**`agent_wrapper.py` change:**

`_build_command(agent, prompt)` gains a required `model` parameter. Always
appends `--model <model>` to the CLI command. The orchestrator passes the
`model` value from the machine JSON role config through to `run_agent`.

**Behavioural notes (Claude vs Gemini):**

- Claude: `--model` is a hard pin — one model for the entire invocation
- Gemini: `--model` with a specific ID is a hard pin (desired); `auto-gemini-3`
  or omitted keeps the per-turn router active (disallowed in machine files)
- See `learning/agent-model-selection.md` for full details

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

### Machine file pinning vs CLI overrides

The `"model"` field in the machine JSON is **required** and defines the pinned
model for every production run. Machine files encode the exact configuration —
agent and model — that is known-good and reproducible.

CLI overrides are the **only sanctioned way** to deviate from pinned models,
intended for testing a new model without editing machine files:

```bash
# Standard run — uses model from machine JSON
python3 orchestrator.py --state-machine machines/default-gemini.json ...

# Test a specific model without a dedicated machine file
python3 orchestrator.py \
    --state-machine machines/default-gemini.json \
    --model-override "ARCHITECT=gemini-3-flash-preview" \
    --model-override "TESTER=gemini-2.5-flash-lite" ...
```

Or a global override applying to all AI roles:

```bash
--agent claude --model claude-opus-4-6
```

This keeps machine files focused on pipeline structure (transitions, roles,
history policy) and avoids a combinatorial explosion:

```
machines/default.json          (Claude, TM — standard)
machines/simple.json           (Claude, simple — standard)
machines/default-gemini.json   (Gemini, TM — standard)
machines/simple-gemini.json    (Gemini, simple — standard)
```

No additional files needed to test Opus vs Sonnet or flash-preview vs
flash-lite — that's what overrides are for.

### Model usage tracking in metrics

`run-metrics.json` currently records `agent` (claude/gemini) and token counts
per invocation. This is insufficient once model selection is in play — Gemini's
per-turn routing means multiple specific models can be used within a single
invocation, each with different token costs.

The metrics schema needs to be extended to capture:

**Per-invocation:**
```json
{
  "role": "IMPLEMENTOR",
  "agent": "gemini",
  "model": "gemini-3-flash-preview",
  "tokens_in": 37454,
  "tokens_out": 2179,
  "tokens_cached": 77465,
  "model_breakdown": {
    "gemini-2.5-flash-lite":  { "tokens_in": 3200, "tokens_out": 45,   "tokens_cached": 0     },
    "gemini-3-flash-preview": { "tokens_in": 34254,"tokens_out": 2134, "tokens_cached": 77465 }
  }
}
```

**Aggregated in run summary:**
- Per-agent totals (claude vs gemini) — existing behaviour, keep
- Per-specific-model totals across the full run (e.g. total tokens consumed
  by `gemini-3-flash-preview` across all invocations)
- Grand total across all agents and models

The `model_breakdown` field is sourced from Gemini's `stats.models` in the
result event (already available). For Claude, `model_breakdown` is omitted or
contains a single entry matching the configured model.

`AgentResult` in `agent_wrapper.py` needs a `model_breakdown: dict` field to
carry this data from the result event through to `metrics.py`.

### Documentation requirement

`machines/README.md` must be updated as part of this task to document:
- The `"model"` field as required — what happens if it is missing or set to an
  auto-routing value (schema validation error)
- Claude hard-pin vs Gemini pinned-model behaviour
- The CLI override flags and that they are the only sanctioned escape hatch
- The pinning design principle: machine files must be fully reproducible
