# Subtask: create-oracle-phase-types-doc

| Field    | Value                |
|----------|----------------------|
| Status   | —                    |
| Epic     | main             |
| Tags     | —             |
| Parent   | b1c374-document-oracle-and-n-phase-model           |
| Priority | —         |

## Description

Create `ai-builder/oracle/phase-types.md` documenting all 6 phase types.

For each phase, document:
- Participants (which roles are involved)
- Whether a pipeline run occurs
- Purpose
- Pipeline behaviour (what the pipeline does internally, if applicable)
- Inputs and outputs
- Transition conditions (what triggers entry, what comes next)

The 6 phases:
1. Discovery — Oracle + Human, no pipeline run
2. Planning — Oracle + ARCHITECT + TM, pipeline run (decompose mode)
3. Human Review (Plan) — Oracle + Human, no pipeline run
4. Implementation — Oracle + all pipeline roles, pipeline run per atomic subtask
5. Human Review (Implementation) — Oracle + Human, no pipeline run
6. Re-planning — Oracle + ARCHITECT + TM, pipeline run (revise existing task tree)

Source: "Phase Types" section of
`sandbox/brainstorm-oracle-and-n-phase-pipeline.md`.

## Notes

_None._
