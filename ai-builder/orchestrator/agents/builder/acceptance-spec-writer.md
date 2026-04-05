# ACCEPTANCE_SPEC_WRITER

Claude-powered pipeline stage. Runs once, before any ARCHITECT stage. Reads
the build spec (job document) and writes two files to the output directory that
anchor the API contract for all downstream agents.

## Outputs

| File | Path | Purpose |
|------|------|---------|
| `acceptance-spec.md` | `<output_dir>/acceptance-spec.md` | Human-readable verbatim copy of the API contract. Read by ARCHITECT (DECOMPOSE and TOP integrate modes). |
| `acceptance-spec.json` | `<output_dir>/acceptance-spec.json` | Machine-readable endpoint list. Read by the spec coverage checker. Must validate against `acceptance-spec-schema.json`. |

## Outcomes

| Outcome | Meaning |
|---------|---------|
| `ACCEPTANCE_SPEC_WRITER_DONE` | Files written. Pipeline proceeds to ARCHITECT. |
| `ACCEPTANCE_SPEC_WRITER_EMPTY_SPEC` | No endpoints found — spec is empty, placeholder, or HTTP but unreadable. Pipeline halts. |
| `ACCEPTANCE_SPEC_WRITER_UNSUPPORTED_INTERFACE` | Build spec contains a non-HTTP interface. Pipeline halts. |

## Role prompt

`ai-builder/orchestrator/machines/builder/roles/ACCEPTANCE_SPEC_WRITER.md`

## Agent type

`claude` — runs via `agent_wrapper.run_agent()` with `--allowedTools Read,Edit,Write,Bash`.

## State machine

Registered in `machines/builder/default.json`. Runs as the `start_state`
before ARCHITECT. `build_prompt()` in `orchestrator.py` has a special case for
this role that injects the job doc path, output dir, and custom valid outcomes
(`ACCEPTANCE_SPEC_WRITER_DONE | ACCEPTANCE_SPEC_WRITER_UNSUPPORTED_INTERFACE`).

## Non-HTTP interfaces

If the build spec describes any non-HTTP interface (CLI, gRPC, message queue,
library API, etc.), the agent halts with
`ACCEPTANCE_SPEC_WRITER_UNSUPPORTED_INTERFACE`. The error message tells the
user which interface type was detected and that a new schema + writer/checker
pair must be defined before running this build spec through the pipeline.

## Convention

Both output files are written to a known path in `output_dir`. No path
injection by the orchestrator is needed — downstream agents locate them by
convention.
