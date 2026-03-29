# Learning: Format Choices — XML for AI Output, JSON for State, Markdown for Interface

**Context:** Discovered while designing and iterating on the ai-builder pipeline
communication architecture. The pipeline has three distinct layers, each with
different consumers and different requirements that led to three different format
choices.

---

## The Three Layers

### AI agent output: XML

AI agents (ARCHITECT, IMPLEMENTOR) emit a `<response>` XML block as the final
content of their response. XML was chosen over JSON because AI model output
naturally contains content that is hard to escape correctly in JSON: multiline
prose, shell commands with `&&`, Go generics like `map[string]User`, markdown
code blocks, and backticks. JSON fenced blocks caused repeated parse failures
when models emitted unescaped newlines or special characters inside string values.

XML's self-delimiting tags let the model write raw content without thinking
about escaping at all. The orchestrator uses a simple regex tag extractor
(`_extract_xml_tag`) — fault-tolerant, no DOM parser needed.

**Why XML and not JSON — historical context:**

XML may seem like an odd choice given that it largely fell out of fashion after
JSON displaced it for APIs and config (2012–2016, partly due to SOAP/enterprise
era bloat). The choice here is not about XML's enterprise features — it is
purely about delimiter robustness for heterogeneous text content. Think heredocs,
not SOAP.

**Caveat:** XML entity encoding (`&amp;`, `&lt;`) must be decoded after
extraction. Models occasionally emit entity-encoded content inside tags (e.g.
`&amp;&amp;` instead of `&&` in a shell command). This is fixed with one
`html.unescape()` call at parse time — simpler than prompt-engineering models
to escape JSON correctly.

### Orchestrator input state: JSON (task.json)

The orchestrator reads pipeline state exclusively from `task.json` files in the
task tree. `task.json` is the authoritative record: goal, context, complexity,
level, depth, output_dir, design, acceptance_criteria, test_command, and
execution metrics all live here. Markdown READMEs are never parsed as input
state.

JSON is the right format here because this content is written and read by
deterministic code — scripts and Python functions that need an exact schema,
finite valid values, and reliable parsing. Markdown is the wrong format for
machine-readable state (see `separate-prose-from-structured-data.md`).

### Markdown: output projection and human/AI interface

Markdown (`README.md` and companion `.md` files) serves two related roles:

1. **Output projection** — README files in the output directory and task tree
   are generated views of the internal state, not the state itself. They are
   written by ARCHITECT (content) and rebuilt/indexed by DOCUMENTER agents
   (formatting). The orchestrator regenerates them as a post-completion step.
   They are never parsed back as input.

2. **Human/AI interface** — job documents, role prompts, design docs, companion
   docs, task READMEs. Markdown is the format AI models read and write naturally,
   and humans can read without tooling.

---

## Summary

| Layer | Format | Consumer | Reason |
|-------|--------|----------|--------|
| AI agent output | XML `<response>` block | Orchestrator parser | Robust delimiter; no escaping of prose/code |
| Pipeline state | JSON (`task.json`) | Orchestrator, scripts | Structured, typed, schema-enforced |
| Docs / README | Markdown (projection) | Humans, AI agents | Readable by both; never parsed as state |
| Human/AI interface | Markdown | Humans, AI agents | Natural language format for both |

---

## The Principle

**Match the format to the consumer and the write-time constraints.**

- If a machine writes it and a machine reads it: JSON.
- If an AI writes it and a machine must parse it: XML (robust delimiters beat escaped strings).
- If a human or AI writes it for human or AI reading: Markdown.

Markdown as state representation — the original design — optimises for neither
machine parsing nor AI writing. Separating the layers eliminated an entire class
of parse failures.
