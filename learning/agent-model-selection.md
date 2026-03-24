# Agent Model Selection

## Overview

Both the Claude CLI and Gemini CLI support model selection via a `--model` flag.
The pipeline currently pins neither — both use their respective CLI defaults.
This document covers how each agent handles model selection, the behavioral
differences, and what per-role model configuration would look like.

---

## Claude

### Mechanism

Claude uses a single model for the entire invocation. Pass `--model <id>` to
pin it; omit it to use the CLI default (currently `claude-sonnet-4-6`).

```bash
claude --model claude-opus-4-6 --output-format stream-json -p "..."
```

### Available models (as of 2026-03)

| Model ID | Notes |
|----------|-------|
| `claude-opus-4-6` | Most capable, highest cost |
| `claude-sonnet-4-6` | Balanced — current CLI default |
| `claude-haiku-4-5-20251001` | Fastest, lowest cost |

### Observability

The result event doesn't include a per-model breakdown because only one model
is ever used. You know which model ran from what you configured.

### Key characteristic

**One model, entire invocation.** No per-turn switching. Pinning `--model` is
a hard guarantee.

---

## Gemini

### Mechanism

Gemini also supports `--model <id>` to pin a specific model. Without it, the
Gemini CLI defaults to an auto-routing mode (currently `auto-gemini-3`) that
selects the model **per turn** within a session based on perceived complexity.

```bash
gemini --model gemini-3-flash-preview --output-format stream-json -p "..."
```

### Auto-routing (`auto-gemini-3`)

When no model is specified, Gemini routes each turn to one of its available
models. Observed behavior from pipeline runs:

- `gemini-2.5-flash-lite` — routed for simpler turns (short responses, quick
  tool calls)
- `gemini-3-flash-preview` — routed for heavier reasoning turns

The routing algorithm is internal to the Gemini CLI and not publicly documented.
The likely inputs are prompt/context length and perceived complexity. You cannot
predict or control which model handles a given turn.

### Observability

The `result` event's `stats.models` field shows a per-model token breakdown
for the entire invocation:

```json
"stats": {
  "total_tokens": 97616,
  "models": {
    "gemini-2.5-flash-lite":  { "total_tokens": 3343,  "input_tokens": 3173,  "output_tokens": 32 },
    "gemini-3-flash-preview": { "total_tokens": 94273, "input_tokens": 91408, "output_tokens": 80 }
  }
}
```

Two keys = model switching occurred at least once. One key = single model used
throughout. You cannot tell from this event when or how many times the switch
happened.

### Key characteristic

**Per-turn routing when using auto mode.** Pinning `--model` to a specific ID
gives Claude-like behaviour (one model, entire invocation). Pinning to an
`auto-*` value keeps the per-turn router active.

---

## Comparison

| | Claude | Gemini |
|---|---|---|
| Default model | `claude-sonnet-4-6` | `auto-gemini-3` (per-turn router) |
| Model switching within invocation | No — one model always | Yes — if using auto mode |
| Pin a specific model | `--model <id>` | `--model <id>` |
| Pin auto-routing explicitly | N/A | `--model auto-gemini-3` |
| Per-model token breakdown in result | No | Yes (`stats.models`) |
| Semantics of pinning | Hard guarantee | Hard if specific model; routing hint if `auto-*` |

---

## Per-role model configuration (planned)

Adding a `"model"` field to each role in the machine JSON would allow
per-role model selection without code changes:

```json
"roles": {
  "ARCHITECT":   { "agent": "claude",  "model": "claude-opus-4-6",          ... },
  "IMPLEMENTOR": { "agent": "gemini",  "model": "gemini-3-flash-preview",    ... },
  "TESTER":      { "agent": "gemini",  "model": "gemini-2.5-flash-lite",     ... }
}
```

Omitting `"model"` falls back to the CLI default (current behaviour).

The `model` field would be passed as `--model <value>` in `_build_command`.
For Claude it means a hard model pin. For Gemini, specifying `auto-gemini-3`
or omitting the field entirely both yield per-turn auto-routing; specifying a
concrete model ID (e.g. `gemini-3-flash-preview`) pins the model for the
full invocation.

The machine JSON specifies the **default model for standard operation**. CLI
overrides (`--model-override ROLE=model`) are for testing specific cases without
creating additional machine files. See task `4f9fba-add-model-selection-to-machine-config`
for full implementation details including the metrics tracking design.
