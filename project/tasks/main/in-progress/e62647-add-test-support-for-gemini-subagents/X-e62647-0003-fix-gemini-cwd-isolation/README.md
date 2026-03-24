# Task: fix-gemini-cwd-isolation

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | e62647-add-test-support-for-gemini-subagents             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Prevent Gemini agents from loading `CLAUDE.md` and exploring the repo by using
a per-invocation temp directory with a scoped `GEMINI.md` as the subprocess cwd.

## Context

`cwd=/tmp` prevents Claude from loading `CLAUDE.md` at startup (Claude walks up
from cwd to find config files). For Gemini, `cwd=/tmp` prevents `GEMINI.md` from
loading at startup, but Gemini is far more exploratory at runtime — once it has
an absolute path to the job doc (which lives in the repo), it traverses the repo
structure, finds `CLAUDE.md`, and follows Oracle instructions instead of pipeline
agent instructions.

Confirmed failure (2026-03-23): Gemini ARCHITECT read `CLAUDE.md`, decomposed a
fibonacci task following Oracle TM conventions, modified the committed job document,
and emitted `ARCHITECT_DECOMPOSITION_READY` instead of `ARCHITECT_DESIGN_READY`.

Gemini reads `GEMINI.md` from its cwd at startup as session configuration. The fix:
create a unique temp dir per invocation, write a scoped `GEMINI.md` to it, use it
as the subprocess cwd, and clean up after exit. This gives Gemini the right
instructions before it starts any tool use.

**Changes to `agent_wrapper.py`:**

In `run_agent`, when `agent == "gemini"`:
1. Create `tmpdir = tempfile.mkdtemp()` instead of using `/tmp` directly
2. Write `GEMINI.md` to `tmpdir`
3. Use `tmpdir` as `cwd` in `subprocess.Popen`
4. Delete `tmpdir` in a `finally` block after the process exits

Claude's path is unchanged — it continues using `cwd=Path("/tmp")`.

**`GEMINI.md` content:**

The GEMINI.md should scope Gemini to pipeline agent behavior:
- You are a focused pipeline agent executing a specific role
- Follow ONLY the instructions in your prompt
- Do not read `CLAUDE.md` or any project configuration files
- Do not explore directory structures outside paths explicitly given in your prompt
- Do not read session status files or task management files

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
