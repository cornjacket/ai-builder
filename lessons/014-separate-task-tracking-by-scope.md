# Lesson 014: Separate Task Tracking by Scope, Not by Repo Count

## Context

In a multi-repo project, all task documents initially lived in a single repo (`platform-services/tasks/`). As the project grew, some tasks didn't fit — workspace reorganization, cross-repo process changes, and project-level concerns had no natural home alongside service code tasks.

## Problem

Forcing all tasks into one directory creates a false association between the task and the repo it lives in. AI agents loading `platform-services/tasks/` for context get irrelevant workspace-level tasks mixed in with code tasks. Developers looking for "how do I restructure the workspace" shouldn't have to search a directory full of service implementation specs.

## Solution

Create task directories scoped by concern, each with independent numbering:

| Directory | Scope |
|-----------|-------|
| `platform-services/tasks/` | Code, tests, service-level docs |
| `platform-docs/tasks/` | Workspace structure, cross-repo concerns, project process |

The key insight: scope the directory to the *type of change*, not the number of repos affected. A task that touches three repos but is fundamentally about service behavior belongs in platform-services. A task that touches one repo but is about workspace organization belongs in platform-docs.

## Decision Guidance

When deciding where a task belongs, ask: "Is this about how the software works, or how the project is organized?" Code behavior → services. Project structure → docs.
