# Task: brainstorm-gemini-as-frontend-ai

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | gemini, oracle, frontend, design               |
| Priority    | HIGH           |
| Next-subtask-id | 0000               |

## Goal

Brainstorm and evaluate Gemini CLI as the front-end AI (Oracle) for
ai-builder development workflows. Determine what it can do effectively,
where it falls short compared to Claude, and whether it is a viable driver
of the development loop that ai-builder itself is built with.

## Context

The Oracle role (`37a660-design-oracle-and-pipeline-phases`) is the
human-facing AI that conducts discovery, manages task planning, coordinates
pipeline phase transitions, and submits jobs to the back-end orchestrator.
Today that role is filled interactively by Claude Code (this session). The
question is whether Gemini CLI could fill it — either as an alternative or
complement.

Gemini is already supported as a pipeline back-end agent (e62647). The
question here is the front-end: can Gemini drive the *development* of
ai-builder itself — reading the codebase, navigating the task system,
writing and editing files, making decisions — with the same effectiveness?

**Questions to explore:**

1. **Context window and codebase navigation** — Gemini has a 1M token
   context window. Can it hold more of the ai-builder codebase in context
   at once than Claude's 200K? Does this reduce the need for targeted
   file reads?

2. **Task system interaction** — Can Gemini reliably use the task
   management scripts (`new-user-task.sh`, `complete-task.sh`, etc.) and
   navigate the `project/tasks/` tree without going off-script?

3. **GEMINI.md vs CLAUDE.md** — We know Gemini explores absolute paths
   and loads GEMINI.md from its cwd. Can this be used to scope Gemini to
   ai-builder development workflows cleanly?

4. **Code editing quality** — How does Gemini compare to Claude for
   Python edits in `orchestrator/`, shell script edits, and Markdown
   documentation tasks?

5. **Session persistence** — Gemini's per-turn auto-routing (`auto-gemini-3`)
   means heavier reasoning turns get a more capable model. Does this make
   it cost-effective for the mixed workload of a development session
   (some trivial file reads, some complex design decisions)?

6. **Heredoc / tool execution reliability** — Known issue from the
   user-service regression: `gemini-3-flash-preview` had parse errors on
   heredoc shell syntax. Would this affect development workflows that
   write files?

7. **Parallel roles** — Could Gemini serve as front-end Oracle while
   Claude serves as back-end pipeline agent (or vice versa), leveraging
   each model's strengths?

**Relationship to `37a660`:** This brainstorm informs the Oracle design.
If Gemini is viable as the front-end, the Oracle architecture should be
model-agnostic. If it has gaps, those gaps should shape the Oracle's
design constraints.

**Reference:** `learning/agent-model-selection.md`,
`learning/agent-cwd-and-context-isolation.md`

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
