# Task: doc-pipeline

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | in-progress |
| Epic        | main               |
| Tags        | pipeline, documentation               |
| Priority    | MED           |
| Next-subtask-id | 0010 |

## Goal

Implement a documentation generation pipeline that traverses an existing source
tree and produces structured `.md` documentation alongside source files. This is
the first repurposing of the build pipeline as a general-purpose tree-traversal
framework: a new `doc.json` machine file + doc-specific role prompts, with the
orchestrator infrastructure unchanged.

## Context

Brainstorm: `sandbox/brainstorm-pipeline-repurposing.md`

The doc pipeline uses the same recursive task tree, frame stack, DECOMPOSE_HANDLER,
and handoff history as the build pipeline. New elements needed:

- `doc.json` machine file
- Role prompts: DOC_ARCHITECT (decompose + atomic modes), DOC_INTEGRATOR
- POST_IMPLEMENT_HANDLER configured with a Markdown linter (checks required
  sections exist, no empty files)
- `"type": "file"` component support in DECOMPOSE_HANDLER (see 49352f-0003/0004)
- Level-scoped handoff history (see 49352f-0005) for correct integrate context

**Role mapping:**

| Role | Job |
|------|-----|
| DOC_ARCHITECT (decompose) | Scan directory, identify sub-components and parent-level source files, generate directory-level docs, return components JSON |
| DOC_ARCHITECT (atomic) | Read all source files in a leaf component, generate component-level docs |
| POST_IMPLEMENT_HANDLER | Markdown linter — required sections exist, no empty files |
| DOC_INTEGRATOR | Read sub-component docs + parent-level source files, produce cross-component synthesis, rebuild directory README index |

Output: permanent companion `.md` files throughout the source tree. No scratch
pad / no cleanup (unlike review/update pipelines).

**Depends on:** 49352f subtasks 0003, 0004, 0005 (file-type components + handoff frame stack).

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-b9529c-0000-extend-lch-route-on](X-b9529c-0000-extend-lch-route-on/)
- [x] [X-b9529c-0001-decompose-handler-component-type](X-b9529c-0001-decompose-handler-component-type/)
- [x] [X-b9529c-0002-doc-machine-json](X-b9529c-0002-doc-machine-json/)
- [x] [X-b9529c-0003-doc-architect-prompt](X-b9529c-0003-doc-architect-prompt/)
- [x] [X-b9529c-0004-doc-integrator-prompt](X-b9529c-0004-doc-integrator-prompt/)
- [x] [X-b9529c-0005-markdown-linter-agent](X-b9529c-0005-markdown-linter-agent/)
- [x] [X-b9529c-0006-unit-tests](X-b9529c-0006-unit-tests/)
- [ ] [b9529c-0007-regression-test](b9529c-0007-regression-test/)
- [ ] [b9529c-0008-documentation](b9529c-0008-documentation/)
- [ ] [b9529c-0009-delete-brainstorm](b9529c-0009-delete-brainstorm/)
<!-- subtask-list-end -->

## Notes

_None._
