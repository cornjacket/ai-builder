# Task: add-project-management-system-template

| Field    | Value                                         |
|----------|-----------------------------------------------|
| Status | in-progress |
| Epic     | main                                          |
| Tags     | project-management, orchestrator, tooling     |
| Parent   | —                                             |
| Priority | HIGH                                          |

## Description

Create a portable, self-contained project management system that can be
installed into any target application repository — including those generated
by the ai-builder orchestrator. The template is a first-class artifact: task
files live inside the same repo as the application they describe, making them
readable by both human developers and AI agents working in that repo.

### Directory structure

The template lives under `target/` in ai-builder:

```
target/
    project/              ← copied as-is into the target repo as project/
        tasks/
            scripts/      ← all task management shell scripts
            README.md     ← generic task system documentation
        status/           ← daily status reports land here
    SETUP.md              ← quick-start guide for new users
    setup-project.sh      ← installs target/project/ into a target repo
    init-claude-md.sh     ← initialises CLAUDE.md in the target repo
```

`setup-project.sh` and `init-claude-md.sh` are installation tools — they
are not copied into the target repo, they run from ai-builder against it.

### Orchestrator integration

The ai-builder orchestrator gains a **PROJECT MANAGER** role that owns
the task system in the target application repo. The PROJECT MANAGER:

- Decomposes a high-level feature request into tasks and subtasks using
  `new-task.sh`
- Sequences work and drives the ARCHITECT → IMPLEMENTOR → TESTER pipeline
  task by task
- Marks tasks complete via `complete-task.sh` when the TESTER signs off
- Maintains the task system as the shared state between all pipeline roles

The task system becomes the **persistent memory** of the pipeline — enabling
multi-session, multi-task projects rather than single-shot code generation.

## Documentation

Document `target/` structure in a `target/SETUP.md`. Document the PROJECT
MANAGER role in `roles/PROJECT_MANAGER.md`.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [ ] [e29682-create-template-skeleton](e29682-create-template-skeleton/)
- [ ] [299a49-write-setup-script](299a49-write-setup-script/)
- [ ] [02767c-write-claude-md-init-script](02767c-write-claude-md-init-script/)
- [ ] [57c541-write-template-readme](57c541-write-template-readme/)
- [ ] [a84be3-design-pm-role](a84be3-design-pm-role/)
- [ ] [cb2735-implement-pm-role](cb2735-implement-pm-role/)
- [ ] [392343-test-template-end-to-end](392343-test-template-end-to-end/)
<!-- subtask-list-end -->

## Notes

The existing `project/tasks/` system in ai-builder itself is the reference
implementation. The template is derived from it, not a parallel design.
