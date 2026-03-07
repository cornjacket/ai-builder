# Lesson 015: Bootstrap Scripts for Multi-Repo Workspaces

## Context

A multi-repo project with symlinks, worktrees, and cross-repo conventions requires setup steps that aren't obvious from reading a README. New users (human or AI) must discover and execute these steps manually.

## Problem

Without a bootstrap script, workspace setup is tribal knowledge. Each new contributor (or AI agent on a fresh machine) faces the same discovery process: which repos to clone, where to put them, what symlinks to create, what services to start. This gets worse as workspace complexity grows (worktrees, bare repos, automation scripts).

## Solution

Create a single bootstrap script at the workspace root that automates the full setup. The script should be idempotent, require no external dependencies beyond git and a shell, and print clear next steps when done.

## Two-Phase Bootstrap Pattern

When the bootstrap script lives inside a repo that it also sets up (e.g., the script is in `platform-docs/tools/` but needs to create the worktree structure that includes `platform-docs/main/`), use a two-phase approach:

1. **Temporary clone** — clone the repo just to access the script
2. **Run bootstrap** — script creates the full workspace (including a proper version of the repo it was cloned from)
3. **Self-cleanup** — script deletes the temporary clone since the workspace version replaces it

This avoids duplicating the script outside the repo or requiring a separate distribution mechanism.

## Decision Guidance

If your project has more than 2 repos or any non-obvious setup steps (symlinks, directory conventions, config generation), create a bootstrap script early. The cost is low and it pays off every time someone sets up the workspace. If the script lives inside one of the repos it configures, use the two-phase pattern to avoid circular dependencies.
