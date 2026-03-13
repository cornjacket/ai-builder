# Open Questions

Unresolved design questions for the ai-builder pipeline. When a question is
resolved, remove it and update the relevant document — do not leave resolved
questions in place.

---

## Orchestrator

**DOCS: field parsing not yet implemented**
`parse_outcome()` currently extracts `OUTCOME` and `HANDOFF` only. The
`DOCS:` field needs to be added to the parser, and the orchestrator loop
needs to conditionally invoke the DOCUMENTER hook based on its value.
Related: `routing.md` — DOCUMENTER hook logic.

**Stub role injection**
The orchestrator has no mechanism to replace a role with a scripted stub
for testing. This blocks deterministic testing of conditional paths like
`NEEDS_ARCHITECT` and `TESTER → FAILED` loops. See task
`e6c37d-add-stub-role-injection-for-pipeline-testing`.

**TM mode start role vs. current code**
`orchestrator.py` still starts at `TASK_MANAGER` in TM mode. The agreed
design starts at `ARCHITECT`. The orchestrator code needs to be updated to
reflect the new design where the Oracle is the entry point and TM only runs
at the end. See task `d9c12f-review-orchestrator-routing-and-flow`.

---

## Decomposition

**New ARCHITECT outcomes not yet implemented**
The decomposition protocol requires `COMPONENTS_READY`, `COMPONENT_READY`,
and `NEEDS_REVISION` outcomes. These are not yet in the ROUTES table or
the orchestrator. See `decomposition.md`.

**How does TASK_MANAGER know which mode it is in?**
Decompose mode vs. design mode needs a signal. Options:
- Job template type signals it (preferred — template = intent)
- Explicit `## Mode:` field in the job document
- Instruction injected by Oracle in the job doc

**Gold verifier for service-level regression tests**
A single-component test (fibonacci) verifies one leaf. A service-level test
needs to verify the assembled output of all components. The gold comparison
strategy for multi-component outputs is not yet designed.

---

## Oracle

**Oracle role definition**
Does the Oracle need a formal `roles/ORACLE.md` prompt file, or is it fully
defined by the target repo's `CLAUDE.md`? Given its scope (discovery, phase
coordination, review management), a dedicated role file is probably warranted.
See `oracle/README.md`.

**Planning tools for ARCHITECT**
What tools should be available to ARCHITECT during Planning that are not
appropriate during Implementation (codebase context, review history,
dependency analysis)? How are they scoped — via `--allowedTools` in the
orchestrator, or a separate Planning role definition?

---

## DOCUMENTER

**DOCUMENTER prompt not yet written**
`roles/DOCUMENTER.md` contains the guideline but not a formal agent prompt.
Needs to be tightened into instructions an AI agent can follow directly.
See task `3e0310-design-documenter-agent`.

**Maximum README size threshold**
What is the threshold that triggers DOCUMENTER to split a README into
sub-files? Line count? Section count? Token estimate? Not yet defined.

**Renamed or moved components**
How does DOCUMENTER handle a component whose directory is renamed or moved?
It needs to update links in parent READMEs without breaking the index.

---

## Subagent CWD Convention

**What CWD should each role be spawned with?**
CLAUDE.md hierarchy loads only for the CWD at launch time — instructing an
agent to "work in `tests/`" after spawning does not load that directory's
CLAUDE.md. The orchestrator needs an explicit convention:
- Always target repo root (simple, loses subdirectory context)
- The directory most relevant to the subtask (correct, requires PM to record
  the path in the job document)
- Deepest common ancestor of all paths the subtask touches

See task `2c2130-design-subagent-cwd-convention`.

---

## `project/reviews/` Structure

What format should review artifacts take? Options:
- Freeform markdown written by Oracle after human review
- Structured format with fields (date, subtask, reviewer, findings, decision)

See task `9b9d18-design-reviews-directory`.
