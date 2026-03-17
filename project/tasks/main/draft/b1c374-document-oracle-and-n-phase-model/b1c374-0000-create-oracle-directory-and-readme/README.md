# Subtask: create-oracle-directory-and-readme

| Field    | Value                |
|----------|----------------------|
| Status   | —                    |
| Epic     | main             |
| Tags     | —             |
| Parent   | b1c374-document-oracle-and-n-phase-model           |
| Priority | —         |

## Description

Create the `ai-builder/oracle/` directory and its `README.md`.

The README should cover:
- What the Oracle is: the human-facing coordinator, front-end to the pipeline,
  continuity layer across sessions
- What it reads: `project/tasks/`, `project/reviews/`, `project/status/`
- What it never does: implement directly
- N-phase model diagram (the outer loop connecting Oracle, pipeline runs, and
  human review)
- Phase index table linking to `phase-types.md`
- File index for the `oracle/` directory

Source: "Core Architecture" and "The N-Phase Model" sections of
`sandbox/brainstorm-oracle-and-n-phase-pipeline.md`.

## Notes

Create the directory first — the README file index will reference other files
in the same directory that don't exist yet; note them as "(planned)".
