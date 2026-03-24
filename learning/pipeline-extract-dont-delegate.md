# Pipeline: Extract and Inline, Don't Delegate

## Principle

When an agent needs a specific piece of information from a document the
orchestrator already holds, the orchestrator should extract and inline that
information directly into the prompt. Do not tell the agent the document path
and leave it to find the information itself.

---

## The anti-pattern

```
The shared job document is at: /absolute/path/to/README.md
```

The agent receives a path, opens the file, reads it, and locates the section
it needs. This is the default pattern in ai-builder and it has two costs:

1. **Wasted AI cycles.** A file read tool call (and sometimes multiple, if the
   agent reads the wrong section first) consumes tokens and latency to retrieve
   information the orchestrator already has in memory. The agent is doing
   mechanical work — parsing a file — that Python can do in microseconds.

2. **Agent tool dependency.** The agent must have a working file read tool that
   can access the path. This assumption breaks under Gemini CLI, whose file
   tool is sandboxed to the launch cwd and cannot read files at absolute paths
   outside it. The same agent behaviour that works with Claude fails silently
   or emits a `NEED_HELP` outcome under Gemini.

---

## The correct pattern

The orchestrator reads the document (it already has a `Path` object), extracts
the relevant section with a regex, and injects it inline:

```python
m = re.search(r'## Test Command\s*\n+(.*?)(?=\n## |\Z)', job_doc.read_text(), re.DOTALL)
if m:
    test_command = m.group(1).strip()
    job_section += f"\n\nTest command:\n```\n{test_command}\n```"
```

The agent receives the value directly. No file open, no parsing, no tool call.

---

## Per-role section mapping

Each role should receive only the sections it actually needs — not the full
document path with an implicit "go read it":

| Role | Sections to inline |
|------|--------------------|
| ARCHITECT | `## Goal`, `## Context` |
| IMPLEMENTOR | `## Goal`, `## Design`, `## Acceptance Criteria`, `## Test Command` |
| TESTER | `## Test Command` only |

The file path can still be included for reference (agents use it for writing
output files and for citing sources in their handoff), but the content should
not require a file read.

---

## Why this matters beyond Gemini

Even with Claude, where the file tool works reliably, delegating extraction
to the agent is wasteful:

- Every TESTER invocation opens the job doc, scans it for `## Test Command`,
  and reads ~1–5KB of content it doesn't need. At 5 TESTER calls per
  platform-monolith run, that is 5 unnecessary tool round-trips.
- If the job doc grows (more sections, larger Design), the agent reads more
  irrelevant content before finding the section it needs.
- Agents occasionally misread or hallucinate section content, especially under
  high context load. Inlining removes the opportunity for this class of error.

---

## General rule

**If the orchestrator already has the data, don't ask an agent to fetch it.**
The orchestrator is Python — it can parse, extract, format, and inject
information in microseconds at zero token cost. Reserve agent tool calls for
work the orchestrator cannot do: running build commands, writing generated
files, making design decisions.
