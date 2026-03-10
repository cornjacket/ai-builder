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

From the `ai-builder` repository root, run both scripts against your target
repository path:

```bash
# Step 1: install the project/ directory
target/setup-project.sh <path-to-target-repo>

# Step 2: initialise CLAUDE.md and GEMINI.md
target/init-claude-md.sh <path-to-target-repo>
```

### Options

`setup-project.sh` accepts an optional `--epic` flag to name the initial epic
(default: `main`):

```bash
target/setup-project.sh <path-to-target-repo> --epic core
```

Both scripts are **idempotent** — running them a second time is safe and will
not overwrite existing files.

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
