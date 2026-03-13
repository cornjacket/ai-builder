# Role: DOCUMENTER

> **Status: DRAFT** — This role definition is a work in progress. The
> guideline below is authoritative for human-driven documentation work now.
> It will be tightened into a formal agent prompt when task
> `3e0310-design-documenter-agent` is worked.

---

## Purpose

The DOCUMENTER owns all documentation. It runs as a post-step hook after
every content-producing role (ARCHITECT, IMPLEMENTOR, TESTER). It does not
invent content — it organises, formats, and maintains the document hierarchy
based on content produced by other roles.

---

## Documentation Guideline

This guideline applies to all directories in the target application and in
ai-builder itself. It defines what gets documented, where it lives, and what
belongs at each level.

> **Note:** The rule below — every directory has a `README.md` — is a
> general repository convention, not just a DOCUMENTER concern. It applies
> to all contributors (human and AI) at all times, regardless of whether
> the DOCUMENTER role is active. It should eventually be promoted to a
> top-level repository standard (e.g. `CLAUDE.md` or a dedicated
> `CONTRIBUTING.md`). It lives here for now as the authoritative draft.

### Every directory gets a `README.md`

**This is a hard rule.** Any directory without a `README.md` is incomplete.
A directory exists to group related things — the README explains what those
things are and why they belong together.

The README is the entry point for the directory. It must answer: *what is
this, what is in it, and how does it fit together?*

**Required sections:**

1. **Purpose** — 1-2 sentences: what this directory contains and why it exists
2. **File index** — table of all files with one-line descriptions
3. **Overview** — data flow, key concepts, how the pieces interact; ASCII
   diagrams welcome
4. **References** — links to detail files for topics that exceed README scope

**Size rule:** when any section exceeds ~50 lines, extract it to a named
detail file, replace the section with a one-line summary and a link.

---

### Every source file gets a companion `.md`

`foo.py` → `foo.md`, `bar.go` → `bar.md`, etc.

**Content:**
- Purpose: what this file does and why it exists
- Inputs and outputs: function signatures, CLI flags, return values
- Key functions/classes and what they do
- Design assumptions and constraints
- Non-obvious behaviour (e.g. side effects, error handling conventions)

Companion files live alongside the source file in the same directory.

**When to update a companion file:**
A companion `.md` must be updated when a code change alters *observable
behaviour* — inputs, outputs, side effects, design assumptions, or
non-obvious behaviour. Internal refactors that preserve the external contract
do not require a doc update.

The IMPLEMENTOR signals this via the `DOCS:` field. If `DOCS:` references a
source file change (e.g. "updated `run_agent()` signature"), the DOCUMENTER
updates the companion. If `DOCS: none`, the companion is left as-is.

---

### Named detail files for topics

When a concept needs more than a paragraph but belongs to this directory's
scope, extract it to a named file: `pipeline-phases.md`, `routing.md`,
`job-format.md`, etc.

- Named by topic, not by source file
- Always referenced from `README.md`
- No subdirectories just to hold detail files — flat is preferred because
  subdirectories require their own `README.md`

---

### What belongs in README vs a detail file

| README | Detail file |
|--------|-------------|
| Data flow diagrams | Specific outcome value tables |
| Role responsibilities (summary) | Full role decision rules |
| Key design decisions | Job template format specs |
| Phase type summaries | Component list format |
| Important pipeline concepts | Open questions |
| File index | Implementation notes |

The README should give a competent reader full situational awareness.
Detail files provide reference material for when they need to go deeper.

---

### What belongs in `open-questions.md`

Unresolved design questions that are not yet captured in a task live in
`open-questions.md` in the relevant directory. Each question should include
enough context to be actionable without referencing a conversation. When a
question is resolved, remove it and update the relevant doc — do not leave
resolved questions in place.

---

### Heading hierarchy

Heading levels are relative within each file, not absolute across the
documentation system. File names and the README file index serve the role
that H1 would serve in a monolithic document — once inside a file, internal
heading hierarchy takes over.

**Convention:**
- **H1** — file topic (appears once, at the top)
- **H2** — major concepts within this file
- **H3** — specific details within a major concept
- **H4** — signal that the file is too large or the concept needs its own file

**In a README specifically:** if a section reaches H3, that is a strong
signal to extract it to a detail file and replace with a one-line summary
and link. H3 in a README means the content is getting too detailed for an
index.

**Navigation contract:** a README's H2 section names should map predictably
to detail file names. If there is a `## Routing` section in the README,
readers — human and AI — should expect `routing.md` to exist. This naming
correspondence lets AIs navigate without reading every file.

---

### Source material hierarchy

When documenting a directory, draw from:

1. **Code** — ground truth; if code and docs disagree, code wins
2. **FLOW.md or equivalent flow docs** — extract relevant sections; once
   absorbed, the source file is deleted
3. **Brainstorm documents** — extract *settled decisions* only; leave open
   questions in `open-questions.md` or task READMEs; brainstorms are
   sandbox artifacts and not versioned

---

## Pipeline Position

DOCUMENTER runs as a mandatory post-step hook after ARCHITECT, IMPLEMENTOR,
and TESTER — not as a node in the ROUTES table. The orchestrator preserves
the pending next role, runs DOCUMENTER, then routes to the pending role.

```
DOCUMENTER_TRIGGERS = {"ARCHITECT", "IMPLEMENTOR", "TESTER"}
```

TASK_MANAGER is excluded — it updates task metadata only and produces no
documentation artifacts.

DOCUMENTER runs only when the triggering role emits a `DOCS:` field in its
output. If `DOCS:` is absent or `none`, the hook is skipped.

---

## What DOCUMENTER Receives

The orchestrator passes:
- Which role just finished
- The job document path
- The output directory path
- The previous role's `HANDOFF:` text
- The previous role's `DOCS:` field (documentation instructions from the
  role that just ran — the content producer is the authority on what needs
  documenting and where)

DOCUMENTER reads artifact files from the output directory directly.

---

## Scope Note

The current intention is to use DOCUMENTER for target application
documentation. Use for ai-builder's own documentation is manual for now,
following the same guideline above.
