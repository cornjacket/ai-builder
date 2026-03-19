# Learning: Design Top-Down Before Building

**Context:** Observed repeatedly while building ai-builder. AI coding tools
make it so fast and frictionless to generate working code that there is a
strong pull toward "vibe coding" — starting immediately, figuring things out
as you go, and letting the design emerge from the implementation.

---

## The Trap

AI coding makes implementation nearly free. You can generate a working script,
a handler, or an entire module in seconds. This removes the traditional cost
that made upfront design worthwhile (hours of manual implementation), and
replaces it with an apparent argument for just starting: "it's so easy, we
can always refactor later."

The result is code that works locally but lacks clear boundaries. Fields bleed
across concerns (pipeline fields in user tasks), formats serve multiple masters
(one README for both AI agents and shell scripts), and scripts grow implicit
dependencies on format details they should never have known about.

Refactoring "later" is also cheap with AI — but only if the bad boundaries
haven't proliferated across many files. Once ten scripts all parse the same
Markdown table the same fragile way, the surface area of the refactor is large
even if each individual change is small.

---

## The Cost

Vibe-coded systems accumulate structural debt that is invisible until you try
to extend them. In ai-builder:

- Mixing prose and metadata in one README file seemed fine until we needed
  DECOMPOSE_HANDLER to parse the Components table reliably — at which point we
  discovered you can't do it without an AI agent.
- Using the same task format for user tasks and pipeline tasks seemed fine until
  we tried to strip pipeline fields from user tasks and found they were
  everywhere.
- Hardcoding `go test ./...` in TESTER.md seemed fine until we needed a
  language-agnostic pipeline and had to re-examine every assumption TESTER made.

Each of these required a task, subtasks, a migration plan, and regression runs
to fix. The cost was not in the fix itself — it was in the discovery, the
analysis, and the careful untangling.

---

## The Discipline

Before building anything non-trivial, identify:

1. **Who are the consumers?** List every system, script, human, or AI agent
   that will read or write this data. They have different needs and different
   failure modes.

2. **What are the boundaries?** Where does one concern end and another begin?
   If two consumers need different formats, they should have different files.
   A boundary is not just a code module — it's a contract between producers
   and consumers.

3. **What is deterministic and what is not?** Deterministic data (structured
   metadata, booleans, enum values) should be owned by code. Non-deterministic
   content (prose, design decisions, acceptance criteria) should be owned by
   humans or AI agents. Don't mix them in the same file.

4. **What will be hard to change later?** File formats, field names, and
   schema structures that are referenced by many scripts are expensive to
   migrate. Lock these down early.

---

## The Principle

**AI makes building cheap. It does not make rethinking cheap.**

The leverage from AI is in execution, not in design. Spending 20 minutes
thinking through consumers, boundaries, and data ownership before writing a
line of code is still one of the highest-leverage activities in software
development — arguably more so now, because the cost asymmetry between
designing and building has increased dramatically.

Vibe your way through a proof of concept. Design top-down before building
anything you'll depend on.
