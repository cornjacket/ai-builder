# Learning

Lessons learned from building and running the ai-builder pipeline. Each file
covers a discrete topic area. These are empirical findings — things we observed
in practice, not just theory.

---

## Index

| File | Topic |
|------|-------|
| [ai-subagent-token-optimization.md](ai-subagent-token-optimization.md) | Reducing token usage and latency for AI subagents in a multi-role pipeline |
| [separate-prose-from-structured-data.md](separate-prose-from-structured-data.md) | Separating AI-written prose from machine-readable structured data in pipeline documents |
| [design-before-building.md](design-before-building.md) | Why top-down design matters more, not less, when AI makes building cheap |
| [agent-cwd-and-context-isolation.md](agent-cwd-and-context-isolation.md) | Why `cwd=/tmp` isolates Claude but not Gemini; Gemini file tool sandbox (read and write); shell command workaround |
| [agent-model-selection.md](agent-model-selection.md) | Model selection for Claude and Gemini — per-turn routing, pinning, and observability differences |
| [pipeline-extract-dont-delegate.md](pipeline-extract-dont-delegate.md) | Orchestrator should extract and inline document content into prompts rather than delegating file reads to agents |
| [pipeline-task-context-ancestry-chain.md](pipeline-task-context-ancestry-chain.md) | How child task `## Context` is built as a labelled ancestry chain to prevent flat-copy duplication at deep nesting |
