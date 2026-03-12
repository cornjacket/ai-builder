# Task: design-documenter-agent

| Field    | Value                                        |
|----------|----------------------------------------------|
| Status   | draft                                        |
| Epic     | main                                         |
| Tags     | documentation, orchestrator, architecture    |
| Parent   | —                                            |
| Priority | HIGH                                         |

## Description

Design the DOCUMENTER agent role for the ai-builder orchestrator pipeline.

**Separation of concerns:**
ARCHITECT and IMPLEMENTOR produce *content* — they know what the system does.
The DOCUMENTER produces *documents* — it owns format, organization, size, and
the index-of-indexes structure. Content producers do not write documents;
the DOCUMENTER does not invent content.

**What the DOCUMENTER does:**
- Creates and formats README.md files from content provided by other roles
- Enforces index-of-indexes structure: non-leaf READMEs contain data flow
  diagrams and component tables; leaf READMEs contain full technical detail
- Judges when a README is too large and splits it into named sub-files,
  updating README.md to link to them
- Incorporates TESTER's acceptance test case documentation into the component
  README (summary + link to test files)
- Maintains consistent formatting and section conventions across all documents

**Pipeline position:**
DOCUMENTER runs after every content-producing role, before TM acts:
```
ARCHITECT → DOCUMENTER → TM creates subtasks
ARCHITECT → DOCUMENTER → IMPLEMENTOR
IMPLEMENTOR → DOCUMENTER → TESTER
TESTER → DOCUMENTER → TM marks complete
```

**Non-leaf README format** (ARCHITECT decompose output):
- Purpose statement
- ASCII data flow diagram
- Component table with links to next level
- No implementation detail

**Leaf README format** (ARCHITECT design + IMPLEMENTOR + TESTER output):
- Purpose and interface contracts
- Data structures and types
- Dependencies
- Usage examples
- Implementation notes
- Link to acceptance test documentation

**Document size management:**
DOCUMENTER is sole judge of whether a document needs splitting. When split:
1. Identify sections that stand alone
2. Create named files (e.g. `architecture.md`, `api-reference.md`)
3. Replace section in README.md with one-line summary + link

**Design questions to resolve:**
- What is the maximum README size before splitting is required? (line count?
  section count? token estimate?)
- What is the minimum viable README for a newly created component directory?
- How does DOCUMENTER handle renamed or moved components?
- Should DOCUMENTER verify existing docs are still accurate, or only create/update?
- How is content passed from ARCHITECT/IMPLEMENTOR/TESTER to DOCUMENTER?
  Via the job document, or by reading the output directory directly?

**Status: DRAFT — requires review before implementation begins.**

## Documentation

Design output: `roles/DOCUMENTER.md`.
Reference: `sandbox/brainstorm-oracle-and-n-phase-pipeline.md` —
"Documentation as First-Class Pipeline Output" section.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

This is a design-only task. Implementation is a separate task to be created
once the design is agreed.

This task should become a subtask of `37a660-design-oracle-and-pipeline-phases`
— the DOCUMENTER is a pipeline role in the N-phase/decomposition model, not a
standalone concern.

Reference: `sandbox/brainstorm-oracle-and-n-phase-pipeline.md` —
sections "Documentation as First-Class Pipeline Output" and
"The DOCUMENTER Role" capture the full design thinking behind this task.
