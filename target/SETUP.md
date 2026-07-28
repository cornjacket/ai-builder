# Project Management System — Setup Guide

This directory contains a portable project management system for use with
AI coding agents (Claude, Gemini, etc.) and human developers. It provides a
structured task tracking workflow that lives inside your repository alongside
your code.

---

## What Gets Installed

Running the setup scripts installs the following into your target repository:

```
project/
    tasks/
        scripts/        — shell scripts for managing tasks
        README.md       — full task system documentation
        main/           — default epic, with status folders:
            inbox/
            draft/
            backlog/
            in-progress/
            complete/
            wont-do/
    status/             — daily status reports (optional)
CLAUDE.md               — AI agent instructions (created or updated)
GEMINI.md               — symlink to CLAUDE.md
```

---

## Installation

From the `ai-builder` repository root, run one script against your target
repository path:

```bash
target/setup-project.sh <path-to-target-repo>
```

That single command installs both layers and writes `CLAUDE.md` / `GEMINI.md`.
The separate `init-claude-md.sh` step is gone: the pinned task-system generator
injects the CLAUDE.md task-tracking block itself, and `setup-project.sh` adds
the `GEMINI.md` symlink alongside it.

### Options

`setup-project.sh` accepts an optional `--epic` flag to name the initial epic
(default: `main`):

```bash
target/setup-project.sh <path-to-target-repo> --epic core
```

Re-running is safe: the script currently declines to touch a target that
already has `project/tasks/`.

---

## First Task

Once installed, create your first task from inside the target repository:

```bash
cd <path-to-target-repo>

project/tasks/scripts/new-task.sh --epic main --folder draft --name my-first-task
```

Then move it to `backlog/` when it's ready to work on:

```bash
project/tasks/scripts/move-task.sh --epic main --name <id>-my-first-task \
    --from draft --to backlog
```

And to `in-progress/` when you start:

```bash
project/tasks/scripts/move-task.sh --epic main --name <id>-my-first-task \
    --from backlog --to in-progress
```

---

## Further Reading

- **`project/tasks/README.md`** — full documentation: task format, status
  directories, all script options, and workflow rules
- **`CLAUDE.md`** — AI agent instructions, including the task management
  workflow rules injected during setup
