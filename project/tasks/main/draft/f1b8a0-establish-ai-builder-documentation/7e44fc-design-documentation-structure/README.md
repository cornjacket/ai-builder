# Task: design-documentation-structure

| Field    | Value                                        |
|----------|----------------------------------------------|
| Status   | —                    |
| Epic     | main                                         |
| Tags     | documentation, architecture                  |
| Parent   | f1b8a0-establish-ai-builder-documentation    |
| Priority | HIGH                                         |

## Description

A design conversation to decide what official documentation the ai-builder
project needs, what form it takes, and how it is organised.

Questions to answer:

**What doc types are needed?**
- Architecture overview — system components, pipeline stages, data flow
- Design spec — detailed behaviour of each role and the orchestrator
- ADRs (Architecture Decision Records) — key decisions made and why
  (e.g. directory-based tasks vs CSV, gold/work separation for regression tests,
  marker-based sed insertion)
- Test documentation — regression test structure, gold/work separation,
  how to add new regression tests

**What topics must be covered?**
- AIDT+ pipeline: ARCHITECT → IMPLEMENTOR → TESTER roles
- Agent wrapper and stream-json event handling
- Regression test framework (Go build tags, gold/work separation)
- Project management system (task structure, scripts, conventions)
- Prompt engineering guidelines (anti-gaming rules, role boundaries)

**How should docs be structured?**
- Where do they live? (`docs/` at repo root is conventional)
- How do we use an **index of index of READMEs** to document each layer of
  the design? Each component directory has its own `README.md`; a top-level
  `docs/INDEX.md` links to each, providing a navigable map of the entire system
  that both humans and AI agents can traverse
- What is the relationship between `docs/` and `CLAUDE.md`? CLAUDE.md should
  be a short orientation file that points into `docs/`

**Index of index of READMEs pattern:**
Each layer of the system has a README that describes that layer. A root-level
index links to each layer's README, which in turn links to its sub-components.
This creates a tree of documentation that mirrors the directory tree, is always
co-located with the code it describes, and is trivially traversable by AI agents
without needing any special tooling.

## Documentation

Output of this task: a decided documentation structure written up as
`docs/DOCUMENTATION-PLAN.md` (itself a draft until reviewed).

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
