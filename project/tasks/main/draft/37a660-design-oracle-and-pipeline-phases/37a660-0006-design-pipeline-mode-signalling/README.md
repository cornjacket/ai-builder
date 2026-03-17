# Subtask: design-pipeline-mode-signalling

| Field    | Value                |
|----------|----------------------|
| Status   | —                    |
| Epic     | main             |
| Tags     | oracle, orchestrator, design             |
| Parent   | 37a660-design-oracle-and-pipeline-phases           |
| Priority | MED         |

## Description

Design how the orchestrator and pipeline roles know which phase mode they are
operating in (Planning vs Implementation vs other future modes).

Currently the pipeline has no concept of mode — the TM role interprets intent
from the job document's TM instruction text. For N phases this needs to be
more explicit and reliable.

**Options to evaluate:**

| Option | Pros | Cons |
|---|---|---|
| TM instruction in job doc (current) | Flexible, Oracle crafts per phase, no code changes | Fragile — depends on Oracle writing good prompts; TM must parse intent from prose |
| `## Mode: plan \| implement` field in job doc | Explicit, structured, no CLI changes | Oracle must set it correctly; adds a required field to JOB-TEMPLATE.md |
| `--mode plan\|implement` CLI flag | Unambiguous, enforced at orchestrator level | Requires CLI change; Oracle must pass it correctly |
| Separate orchestrator entry points | Maximum clarity, no ambiguity | More complex, harder to extend for N phases |

**Updated direction (2026-03-16):** The `## Mode` field in the job document
remains a reasonable signal, but the framing has shifted. ROUTES and AGENTS
are moving toward external configuration files (see `2faff3` and the pipeline
flexibility brainstorm). Mode signalling should be designed with that in mind:
Planning mode is a different ROUTES config, not a hardcoded branch in
`orchestrator.py`.

**Questions to resolve:**

- Does mode affect only the TM, or does it also change ARCHITECT behaviour
  (allowed tools, available outcomes)?
- Can a single pipeline run span multiple modes, or is mode fixed per run?
- Is mode best expressed as a separate ROUTES config file, a `## Mode` field
  in the job doc, or a `--mode` CLI flag? Must be consistent with the
  external config direction.
- How does this interact with `2faff3-add-configurable-start-state-and-routes`?

**Deliverables:**

- A decision on mode signalling consistent with the external config direction
- Updated orchestrator or config format to support Planning mode routes
- Updated Oracle role (`roles/ORACLE.md`) with instructions on setting mode
- Updated `ai-builder/FLOW.md` to document the mode field

## Notes

Tightly coupled with `918f07-design-planning-mode-outcomes` — should be
designed and implemented together.
