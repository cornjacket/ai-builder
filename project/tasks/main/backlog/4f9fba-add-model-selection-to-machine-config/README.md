# Task: add-model-selection-to-machine-config

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | gemini-compat          |
| Next-subtask-id | 0000               |

## Goal

Add an optional `"model"` field to the machine JSON role config so that each
role can specify which model to use, independently of the agent. Omitting the
field falls back to the CLI default (current behaviour).

**Reference:** [`learning/agent-model-selection.md`](../../../../../learning/agent-model-selection.md)

## Context

Both Claude and Gemini CLIs support `--model <id>`. Currently the pipeline
passes no `--model` flag to either, so both use their CLI defaults
(Claude: `claude-sonnet-4-6`; Gemini: `auto-gemini-3` per-turn router).

Per-role model selection enables:
- Pinning expensive roles (ARCHITECT) to a capable model while using a cheaper
  model for TESTER
- Pinning Gemini to a specific model for reproducible benchmarks instead of
  auto-routing
- Mixing agents and models across roles in a single pipeline run

**Machine JSON change:**

```json
"roles": {
  "ARCHITECT":   { "agent": "claude",  "model": "claude-opus-4-6",       ... },
  "IMPLEMENTOR": { "agent": "gemini",  "model": "gemini-3-flash-preview", ... },
  "TESTER":      { "agent": "gemini",  "model": "auto-gemini-3",          ... }
}
```

**`agent_wrapper.py` change:**

`_build_command(agent, prompt)` gains an optional `model` parameter. When
provided, appends `--model <model>` to the CLI command. The orchestrator passes
the `model` value from the machine JSON role config through to `run_agent`.

**Behavioural notes (Claude vs Gemini):**

- Claude: `--model` is a hard pin — one model for the entire invocation
- Gemini: `--model` with a specific ID is a hard pin; `auto-gemini-3` or
  omitted keeps the per-turn router active
- See `learning/agent-model-selection.md` for full details

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

### Machine file defaults vs CLI overrides

The `"model"` field in the machine JSON defines the **default model for
standard operation**. Machine files encode the intended configuration for
normal pipeline runs — the model choices that are known-good and repeatable.

CLI overrides are for **testing specific cases** without creating new files:

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
  "model": "auto-gemini-3",
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
- The `"model"` field in the role config and its default-vs-override semantics
- Claude hard-pin vs Gemini auto-routing behaviour
- The CLI override flags (once designed)
- Guidance: machine files for standard configs, overrides for testing
