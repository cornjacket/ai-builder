# Lesson 017: Git Worktrees for Parallel AI Work

**Category:** repo-structure
**Source project:** cornjacket-platform
**Date:** 2026-02-13

## Context

Multi-repo projects with AI agents need a way for multiple agents (or an agent and a human) to work on different features simultaneously without conflicts. Standard clones require separate workspace copies. Git worktrees provide branch-level isolation within a single workspace.

## Lesson

Bare repositories with git worktrees enable parallel feature work across multiple repos:

- Each feature gets its own directory (`platform-<repo>/<branch>/`) across all repos
- Multiple AI agents can work on different branches without interfering with each other
- Humans can work independently on their own feature branch while agents work on another
- Atomic branch creation (all repos or none) prevents partial state

**Unsolved: runtime isolation.** Worktrees solve code isolation but not runtime isolation. Docker containers, database ports, message bus ports, and volume mounts are shared resources. Two feature branches cannot both run `docker-compose up` simultaneously without port collisions and data conflicts. This must be solved separately (e.g., per-branch port offsets, dynamic compose overrides, or namespaced containers).

## Decision Guidance

When building a multi-repo AI workflow that needs parallel feature development, use bare repos with worktrees for code isolation. Budget separately for runtime isolation — worktrees alone are not enough if features need to run locally.

## Related Lessons

- [015](015-bootstrap-scripts-for-multi-repo-workspaces.md) — Bootstrap Scripts for Multi-Repo Workspaces
