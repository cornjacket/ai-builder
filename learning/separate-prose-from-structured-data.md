# Learning: Separate AI-Written Prose from Machine-Readable Structured Data

**Context:** Discovered while designing the ai-builder pipeline task document
format. Initially all task metadata and prose lived in a single `README.md`
using a Markdown metadata table at the top and free-form sections below.

---

## The Insight

A pipeline document has two fundamentally different kinds of content, consumed
by two fundamentally different consumers:

**Prose** — written and read by AI agents. Goal, Context, Design, Acceptance
Criteria, Test Command. This content is non-deterministic: an AI agent produces
it through reasoning, and downstream AI agents interpret it through reading.
It benefits from natural language formatting (Markdown) because that is what
AI models read well.

**Structured metadata** — written and read by scripts and deterministic code.
Status, Complexity, Level, Last-task, Components table. This content is fully
deterministic: it has an exact schema, a finite set of valid values, and is
consumed by shell scripts and Python functions that need to parse and update
it reliably.

Mixing both in one file optimises for neither consumer.

---

## What Goes Wrong When They Are Mixed

**Fragile parsing.** Shell scripts parsing a Markdown table with `grep`/`sed`
break when field values contain characters that conflict with the delimiter
(e.g. `/` in paths). The fix is always a workaround, never a solution.

**AI agents cannot be eliminated from deterministic steps.** The DECOMPOSE_HANDLER
role reads a Markdown Components table and creates subtask directories — a
purely mechanical transformation. But because the Components table was embedded
in a Markdown README, reliable machine parsing required an AI agent. Moving
Components to a JSON array makes the entire role replaceable with ~30 lines
of Python.

**Fields bleed across task types.** When all task types share one format,
every task carries fields from every other task type. Pipeline-specific fields
(`Complexity`, `Level`, `Last-task`) appear in human-owned user tasks where
they are meaningless, and vice versa. Both become bloated.

**Schema is implicit.** A Markdown table has no enforced schema. Fields can
be missing, misspelled, or given invalid values with no validation at write
time. A JSON file can be validated against a schema at creation time.

---

## The Principle

**Give each consumer the format it works best with.**

- AI agents get `.md` — free-form, human-readable, no parsing required.
  They read it as text and write it as text.
- Scripts and deterministic code get `.json` — structured, typed, easily
  parsed, validatable. They never touch the prose file.

The boundary is clean: if a field is written by a human or an AI agent, it
belongs in `.md`. If a field is written by a script or read by a script, it
belongs in `.json`.

---

## Generalisation

This applies beyond pipeline task documents. Any system that mixes human/AI
content with machine-readable metadata in one file will eventually hit the
same friction:

- Configuration files that contain both human commentary and machine-parsed
  directives (INI files, some YAML configs)
- Issue trackers that embed structured fields in free-text descriptions
- Notebooks that mix code, output, and metadata in one JSON blob

The pattern is always the same: one consumer needs structure and predictability;
the other needs expressiveness and flexibility. Serving both from one format
means compromising both.

**Separate the files. Match the format to the consumer.**
