# Regression Test: Template Setup

This test verifies that the ai-builder project management template installs
correctly and that all task management scripts work as expected.

---

## Directory Structure

```
template-setup/
    test.sh      — runs all checks, exits 0 on pass, 1 on failure
    reset.sh     — removes /tmp/ai-builder-target for a clean re-run
    README.md    — this file
```

The test uses `/tmp/ai-builder-target` as its working directory.
It is created fresh at the start of each run and left in place afterwards
for inspection. Run `reset.sh` to remove it before re-running.

---

## What This Tests

| Section | Coverage |
|---|---|
| 1 | `setup-project.sh` installs all expected directories and scripts |
| 2 | `setup-project.sh` is idempotent |
| 3 | `init-claude-md.sh` creates `CLAUDE.md` with task management section and `GEMINI.md` symlink |
| 4 | `init-claude-md.sh` is idempotent — does not duplicate the section |
| 5 | `verify-setup.sh` passes against the freshly installed target |
| 6 | `new-task.sh` creates a top-level task with correct README and status |
| 7 | `new-task.sh --parent` creates a subtask with `—` status and checkbox in parent |
| 8 | `move-task.sh` moves a task from `draft/` to `backlog/`, updating READMEs |
| 9 | `move-task.sh` moves a task from `backlog/` to `in-progress/` |
| 10 | `list-tasks.sh` shows tasks and subtasks at correct depth |
| 11 | `complete-task.sh --parent` marks a subtask `[x]` and updates its Status |
| 12 | `complete-task.sh` moves a top-level task to `complete/`, updating READMEs |

---

## Run Order

**Step 1 — Reset (optional, for a clean re-run):**

```bash
tests/regression/template-setup/reset.sh
```

**Step 2 — Run the test** (from repo root):

```bash
tests/regression/template-setup/test.sh
```

**Expected output:**

```
Results: 28 passed, 0 failed
```
