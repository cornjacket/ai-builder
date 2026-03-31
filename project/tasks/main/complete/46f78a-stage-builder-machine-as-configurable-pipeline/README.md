# Task: stage-builder-machine-as-configurable-pipeline

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Next-subtask-id | 0006 |

## Goal

Reorganise the orchestrator so that all builder-specific artifacts — agent
implementations, role prompt files, and machine configurations — live under
a `builder/` namespace. This establishes the seam needed to define alternative
pipelines without touching shared infrastructure.

## Context

Everything that drives the current pipeline is builder-specific but lives at
the top level of its respective directory. As new machine definitions are
introduced (different test runners, alternate documenter strategies, non-builder
pipelines), the flat layout creates collisions and makes it unclear which files
belong to which machine.

### Target directory structure

```
ai-builder/
  docs/                             # NEW — cross-machine guidelines
    guidelines/
      doc-format.md                 # moved from roles/
      documentation-standards.md   # extracted from roles/DOCUMENTER.md (renamed)

  orchestrator/
    agents/
      base.py / base.md             # shared infrastructure — stays at top level
      context.py / context.md
      loader.py / loader.md
      README.md (updated)
      builder/                      # builder-specific implementations
        __init__.py
        tester.py / tester.md
        documenter.py / documenter.md
        decompose.py / decompose.md
        lch.py / lch.md
        README.md

    machines/
      README.md (updated)
      builder/                      # builder machine — configs + prompts together
        default.json
        simple.json
        default-gemini.json
        simple-gemini.json
        roles/                      # AI agent prompts for this machine
          ARCHITECT.md              # moved from roles/ + doc-format rules inlined
          IMPLEMENTOR.md            # moved from roles/ + doc-format rules inlined
          README.md
        README.md

# roles/ at repo root — deleted after moves complete
# roles/TESTER.md — retired (redundant with agents/builder/tester.md)
# roles/TASK_MANAGER.md — fate decided in subtask 0000
```

### Key ripple effects

- Machine JSON `"impl"` paths: `"agents.tester.TesterAgent"` →
  `"agents.builder.tester.TesterAgent"`
- Machine JSON `"prompt"` paths: `"roles/ARCHITECT.md"` →
  `"ai-builder/orchestrator/machines/builder/roles/ARCHITECT.md"`
- `ARCHITECT.md` and `IMPLEMENTOR.md`: `roles/doc-format.md` references removed;
  missing format rules (Purpose field rules, full header block example, Tags table)
  inlined directly
- `orchestrator.py` `ROLES_DIR` fallback updated
- `CLAUDE.md` reference to `roles/DOCUMENTER.md` updated

### Open question settled in subtask 0000

`TASK_MANAGER.md` fate must be decided before the structural moves begin.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-46f78a-0000-resolve-task-manager-and-documenter-role-files](X-46f78a-0000-resolve-task-manager-and-documenter-role-files/)
- [x] [X-46f78a-0001-move-agent-impls-into-agents-builder](X-46f78a-0001-move-agent-impls-into-agents-builder/)
- [x] [X-46f78a-0002-move-roles-to-ai-builder-roles-builder](X-46f78a-0002-move-roles-to-ai-builder-roles-builder/)
- [x] [X-46f78a-0003-move-machine-configs-to-machines-builder](X-46f78a-0003-move-machine-configs-to-machines-builder/)
- [x] [X-46f78a-0004-update-orchestrator-path-resolution](X-46f78a-0004-update-orchestrator-path-resolution/)
- [x] [X-46f78a-0005-update-companion-documentation](X-46f78a-0005-update-companion-documentation/)
<!-- subtask-list-end -->

## Notes

_None._
