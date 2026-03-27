# Task: xml-structured-output-format

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 49352f-redesign-pipeline-communication-architecture             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Brainstorm and evaluate replacing the current JSON-based agent response
format with XML in places where agents produce structured output consumed by
the orchestrator. Identify which formats (JSON, XML, plain text) are best
suited to each communication boundary in the pipeline, and produce a migration
plan where XML is the better choice.

## Context

The pipeline currently uses three formats for agent-to-orchestrator
communication:

1. **JSON** — terminal fenced ` ```json ``` ` block (ARCHITECT responses).
   Contains structured fields: `outcome`, `handoff`, `components`, `design`,
   `acceptance_criteria`, `test_command`.
2. **Plain `OUTCOME:`/`HANDOFF:` lines** — internal agents (TESTER, LCH, etc.)
3. **Prose** — everything else in the response body

**The JSON problem:** JSON requires syntactically precise use of `{`, `}`,
`[`, `]`, `"`, `:`, and `,`. These characters appear constantly in the code
and prose that agents write, creating noise that increases the probability of
malformed output. A missing comma or an unescaped quote inside a string value
invalidates the entire block. The orchestrator currently hard-errors on
JSON parse failure (subtask 0015).

**Why XML may be better for AI output:**
- Opening/closing tags (`<design>...</design>`) are self-delimiting and
  visually unambiguous — the AI cannot confuse a tag boundary with prose content
- Multi-line string values need no escaping — code blocks, prose, and
  newlines are all valid inside a tag
- Partial/malformed output is easier to recover from — a missing closing tag
  is detectable and gracefully degradable
- Anthropic's own prompt engineering guidance recommends XML tags for
  structured AI output (Claude is trained on XML-heavy data and handles it well)
- Tags are semantically named, making responses self-documenting

**Proposed format (illustrative):**
```xml
<response>
  <outcome>ARCHITECT_DECOMPOSITION_READY</outcome>
  <handoff>One paragraph summarising...</handoff>
  <components>
    <component>
      <name>store</name>
      <complexity>atomic</complexity>
      <source_dir>internal/myservice/store</source_dir>
      <description>...</description>
    </component>
  </components>
</response>
```

**What to brainstorm:**
- Which boundaries benefit most from XML (agent → orchestrator, orchestrator → agent, internal agent output)?
- Are there cases where JSON remains preferable (e.g. task.json persistence, which is machine-read only)?
- Plain text vs XML for `OUTCOME:`/`HANDOFF:` lines — is there a benefit to wrapping those?
- Parser complexity: Python's `xml.etree.ElementTree` vs a lightweight regex extractor vs a dedicated helper
- Migration path: can both formats be supported during transition, or is a flag-day cut-over cleaner?
- Impact on existing role prompts (`ARCHITECT.md`, `IMPLEMENTOR.md`) — how much changes?

**Start with a brainstorm doc** (`sandbox/brainstorm-xml-structured-output.md`)
before any implementation.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
