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

**Recommendation to evaluate:** A `## Mode` field in the job document is
likely the right balance — it is explicit and structured without requiring
a new CLI flag, and it gives the TM clear instructions without relying on
prose interpretation.

**Questions to resolve:**

- Does mode affect only the TM, or does it also change ARCHITECT behaviour
  (e.g. allowed tools, available outcomes)?
- Can a single pipeline run span multiple modes, or is mode fixed per run?
- How does mode interact with `--start-role`? (e.g. starting at ARCHITECT
  in Planning mode vs Implementation mode)

**Deliverables:**

- A decision on the mode signalling mechanism
- Updated `JOB-TEMPLATE.md` if a `## Mode` field is chosen
- Updated `orchestrator.py` and `build_prompt()` to read and act on mode
- Updated `ai-builder/FLOW.md` to document the mode field
- Updated Oracle role (`roles/ORACLE.md`) with instructions on setting mode

## Notes

Tightly coupled with `918f07-design-planning-mode-outcomes` — should be
designed and implemented together.
