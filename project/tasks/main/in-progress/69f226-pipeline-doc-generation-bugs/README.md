# Task: pipeline-doc-generation-bugs

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | in-progress             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Next-subtask-id | 0004 |

## Goal

Fix four documentation generation bugs in the pipeline: a markdown rendering defect
in Purpose/Tags headers, missing README.md files at architecturally relevant directory
levels, missing theory-of-operation.md and composite-level README generation by the
ARCHITECT, and a weak master-index that lacks links and proper scoping.

## Context

Identified after reviewing user-service-output. The pipeline generates docs only at
leaf component level; intermediate composite/package levels have no README. The
master-index is a flat table with no links. The ARCHITECT prompt does not instruct
creation of theory-of-operation.md or composite-level README files. Gold tests do
not currently validate the presence or absence of README files at specific levels.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-69f226-0000-fix-purpose-tags-markdown-rendering](X-69f226-0000-fix-purpose-tags-markdown-rendering/)
- [x] [X-69f226-0001-add-readme-validation-to-regression-gold-tests](X-69f226-0001-add-readme-validation-to-regression-gold-tests/)
- [ ] [69f226-0002-architect-generates-theory-of-operation-and-composite-readme](69f226-0002-architect-generates-theory-of-operation-and-composite-readme/)
- [ ] [69f226-0003-improve-master-index-with-links-and-scoped-headers](69f226-0003-improve-master-index-with-links-and-scoped-headers/)
<!-- subtask-list-end -->

## Notes

_None._
