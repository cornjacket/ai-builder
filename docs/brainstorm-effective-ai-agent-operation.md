# Brainstorm: Effective AI Agent Operation

## Purpose

This document captures the core principles behind running effective AI coding
agents in a multi-agent pipeline. It is a working brainstorm — ideas are not
yet fully resolved or implemented. The goal is to distill what makes the
difference between an AI agent system that degrades over time and one that
stays reliable and coherent across many sessions and jobs.

These principles inform the design of ai-builder: the orchestrator, the role
definitions, the CLAUDE.md hierarchy, the task system, and the review process.

---

## What To Do With These Principles

These are not yet implemented. The intended path:

1. **Now** — use this document to inform design decisions as we build out the
   oracle, pipeline phases, and role definitions
2. **When `f1b8a0-establish-ai-builder-documentation` is picked up** — promote
   the relevant parts to `docs/` as a formal design reference
3. **As each role is designed** — extract actionable rules into the appropriate
   role definition (`roles/PROJECT_MANAGER.md`, `roles/ARCHITECT.md`, etc.)
4. **Do not copy wholesale into CLAUDE.md** — CLAUDE.md carries rules, not
   the reasoning behind them

---

## Principles

### 1. Context Management

**Minimize context rot in subagents.** Each backend agent (ARCHITECT,
IMPLEMENTOR, TESTER) should receive only what it needs for its specific
subtask. Bloated context degrades output quality — the agent loses focus and
starts confusing earlier instructions with current ones. Keep job documents
tight and scoped.

**Recognize context rot in the front-end (Oracle).** Long-running
orchestration sessions accumulate stale context. The Oracle needs to detect
when its own context has drifted — contradictory instructions, forgotten
decisions, outdated state — and either summarize/reset or surface the issue
to the human. This is harder to solve than subagent rot because the Oracle is
the one that would have to catch it in itself.

**Spawn subagents fresh.** Each subagent should start clean. State passes
through structured artifacts (job documents, task READMEs, review files), not
through the subagent's memory from a prior run.

---

### 2. Instruction Hierarchy (CLAUDE.md)

**Need-to-know, layered from broad to narrow.** Higher layers carry
far-reaching rules (language, toolchain, global conventions). Lower layers
carry narrow, local rules (test naming, fixture patterns, how to invoke a
specific script). Each layer only contains what's unique to that scope — no
repetition of parent rules.

**Instructions must be inline, not pointed to.** Agents don't reliably follow
pointers to external documents. If a rule isn't in the loaded CLAUDE.md
context, it may as well not exist.

**Spawning CWD determines what loads.** The hierarchy only works if subagents
are launched from the right directory. This is an orchestrator responsibility,
not something that happens automatically.

**Placement is a planning decision.** Whether a new directory gets its own
CLAUDE.md is decided by the ARCHITECT during job planning, not by setup
scripts. It is part of the review checklist before implementation begins.

---

### 3. Documentation Hierarchy (README.md)

**Index of indexes, abstracted at the top, granular at the bottom.**
High-level READMEs describe what a system is and how its parts relate.
Low-level READMEs describe exactly what a file or directory contains and how
to use it. An agent navigating an unfamiliar codebase should be able to orient
itself top-down without reading source code.

**READMEs are descriptive; CLAUDE.md is prescriptive.** READMEs explain
design and structure for any reader (human or agent doing research). CLAUDE.md
gives orders to an agent about to do work. These should never be conflated.

**READMEs as project memory.** Because agents don't retain memory across
sessions, the README hierarchy is what allows a future agent to reconstruct
intent. A codebase with good READMEs is one where an agent can start fresh
and still make correct decisions.

---

### 4. Structured Handoffs

**State lives in artifacts, not agent memory.** Job documents, task READMEs,
review files, and `project/status/` entries are the durable record. Anything
that isn't written down is lost when the session ends.

**Formal review as a gate, not an afterthought.** Reviews catch structural
mistakes (wrong abstraction boundaries, bad CLAUDE.md placement, incorrect
directory structure) before they propagate through implementation. The review
artifact becomes part of project memory that future agents can consult.

**Stop-after is a last resort.** The pipeline should flow automatically in the
common case. Human intervention is reserved for high-risk, irreversible, or
genuinely ambiguous architectural decisions.

---

### 5. Task Granularity

**Subtasks should be sized for a single agent session.** Too large and context
rot sets in before the work is done. Too small and the overhead of handoffs
dominates. The right size is one coherent unit of work that produces a
verifiable output.

**Verification is built in.** Every job has a TESTER role and acceptance
criteria. The pipeline doesn't declare success — it produces output that is
checked against explicit constraints.

---

## Central Thread

The thread connecting all of these principles:

> Agents are stateless and context-limited, so the system around them has to
> carry the structure, memory, and correctness guarantees that a human
> developer would carry in their head.

The orchestrator, task system, CLAUDE.md hierarchy, README hierarchy, and
review process are all expressions of this single idea.

---

## Open Questions

- How does the Oracle detect its own context rot? What signals indicate drift?
- What is the right subtask size in practice? Is it measurable (token count,
  time, file count) or purely qualitative?
- Should the README hierarchy be machine-queryable (structured frontmatter)
  or purely human-readable markdown?
- How do we validate that the CLAUDE.md hierarchy is correct before a job
  runs, not just after?
