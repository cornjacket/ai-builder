# Task: bug-gemini-agent-cannot-read-job-doc

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | in-progress             |
| Epic        | main               |
| Tags        | gemini, orchestrator, bug               |
| Priority    | HIGH           |
| Category    | gemini-compat          |
| Next-subtask-id | 0009 |

## Goal

Fix all pipeline roles so they do not depend on Gemini's sandboxed file tools.
Inline required content and use fully-qualified commands so agents never need
to call `read_file` or `write_file` for pipeline-managed paths.

## Context

Gemini's `read_file` and `write_file` tools are sandboxed to the agent's temp
cwd. Any attempt to access an absolute path outside that directory is rejected:

```
Path not in workspace: Attempted path "...README.md" resolves outside the
allowed workspace directories: /tmp/ai-builder-gemini-xxx
```

**Fixes applied (2026-03-24):**

| Role | Problem | Fix |
|------|---------|-----|
| ARCHITECT | Called `read_file` to get job doc | Inline Goal, Context, Complexity, Level into prompt |
| ARCHITECT | Called `write_file` to write doc files | Added to `gemini_compat.py`: mandate `printf` via `run_shell_command` |
| IMPLEMENTOR | Called `read_file` to get job doc | Inline Goal, Context, Design, AC, Test Command into prompt |
| TESTER | Role prompt step 1 said "read job doc"; tried `read_file` | Updated role prompt to use inlined command; don't read job doc |
| TESTER | Test command `go test ./...` run from temp cwd | Orchestrator prepends `cd <output_dir> &&` to test command |

**Note on the pipeline redesign:**
Under the proposed JSON-native pipeline architecture
(`49352f-redesign-pipeline-communication-architecture`), job doc content will
live in `task.json` and the orchestrator will read it directly — eliminating
this class of bug entirely. These fixes are bridge solutions for the current
architecture.

See `learning/pipeline-extract-dont-delegate.md` for the general principle.

**Remaining:** Create `ai-builder/orchestrator/gemini_compat.md` documenting
all known Gemini CLI behavioural differences and mitigations.

## Notes

Discovered during user-service Gemini regression run (2026-03-24). ARCHITECT
emitted `ARCHITECT_NEED_HELP` after failing to read the job doc via file tool.
Multiple Gemini regression runs required to surface all five affected cases.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-024459-0000-architect-inline-goal-context](X-024459-0000-architect-inline-goal-context/)
- [x] [X-024459-0001-implementor-inline-all-sections](X-024459-0001-implementor-inline-all-sections/)
- [x] [X-024459-0002-architect-file-write-gemini-compat](X-024459-0002-architect-file-write-gemini-compat/)
- [x] [X-024459-0003-tester-role-prompt-inline-command](X-024459-0003-tester-role-prompt-inline-command/)
- [x] [X-024459-0004-tester-cd-output-dir-in-command](X-024459-0004-tester-cd-output-dir-in-command/)
- [x] [X-024459-0005-architect-prompt-boundary-enforcement](X-024459-0005-architect-prompt-boundary-enforcement/)
- [x] [X-024459-0006-implementor-prompt-inlined-content](X-024459-0006-implementor-prompt-inlined-content/)
- [x] [X-024459-0007-orchestrator-role-specific-outcome-validation](X-024459-0007-orchestrator-role-specific-outcome-validation/)
- [ ] [024459-0008-gemini-regression-verification](024459-0008-gemini-regression-verification/)
<!-- subtask-list-end -->

## Notes

_None._
