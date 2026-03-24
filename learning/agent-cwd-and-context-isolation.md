# Agent CWD and Context Isolation

## The problem

Pipeline agents are spawned as subprocesses with their working directory set to
`/tmp`. This was introduced to prevent Claude from loading the ai-builder
developer `CLAUDE.md` — a file that contains Oracle-level instructions ("run
`complete-task.sh --parent` when done", "read the status file at session start")
that are completely wrong for pipeline agents to follow.

The fix works for Claude. It does not work for Gemini.

---

## Why it works for Claude

The Claude CLI (`claude`) walks **upward from cwd at startup** to find and
inject `CLAUDE.md` files into the system prompt. With `cwd=/tmp`, the walk is:

```
/tmp → /  (no CLAUDE.md found)
```

The developer `CLAUDE.md` at `/Users/david/Go/src/.../ai-builder/CLAUDE.md` is
never reached. Claude's session starts with no project configuration — only the
explicit prompt the orchestrator provides.

Even if Claude encountered a file path inside the repo during its work, it would
read that specific file and nothing more. Claude follows the role prompt
precisely: read the job doc, do the work, emit the outcome.

---

## Why it does not work for Gemini

Gemini does not auto-load `CLAUDE.md`. It looks for `GEMINI.md` at startup
instead. So `cwd=/tmp` doesn't help or hurt on that front.

The problem is different: **Gemini is exploratory**. When the ARCHITECT prompt
contains an absolute path to a job document (which lives inside the repo),
Gemini:

1. Tries to read the job doc — but first tries relative paths in `/tmp`, fails
2. Searches `/tmp` for relevant files
3. Discovers the repo path from the absolute path in the prompt
4. Explores the repo directory structure
5. Finds and reads `CLAUDE.md`
6. Treats it as authoritative context — reads status files, follows task
   management instructions, decomposes tasks using Oracle conventions

In a confirmed regression run (2026-03-23), this caused the ARCHITECT to:
- Spend ~15 tool calls on project context-gathering before doing any work
- Modify the committed job document (`JOB-fibonacci-demo.md`) by writing a
  `## Components` section back to disk
- Emit `ARCHITECT_DECOMPOSITION_READY` because it was following Oracle TM
  instructions rather than pipeline agent instructions

The `cwd=/tmp` fix is about preventing **auto-loading at startup**. It does
nothing to prevent **active file exploration at runtime via tool use**.

---

## The fix

The correct isolation mechanism for Gemini is a `GEMINI.md` file written to the
subprocess's cwd before launch. Gemini reads `GEMINI.md` at startup as its
session configuration, equivalent to how Claude reads `CLAUDE.md`. A focused
`GEMINI.md` can override any project-level configuration Gemini might otherwise
pick up by exploration.

Implementation:
- Create a `tempfile.mkdtemp()` per agent invocation instead of using `/tmp` directly
- Write a `GEMINI.md` to that directory containing agent-scoped instructions
- Use the temp dir as `cwd`
- Clean up after the subprocess exits

The `GEMINI.md` should tell Gemini: you are a focused pipeline agent; follow
only the instructions in your prompt; do not read configuration files from other
directories.

---

## Key distinction

| | Claude | Gemini |
|---|---|---|
| Config file at startup | `CLAUDE.md` (walks up from cwd) | `GEMINI.md` (in cwd) |
| `cwd=/tmp` prevents config loading | ✓ Yes | ✓ Yes (for GEMINI.md) |
| Active exploration via tools | Minimal — follows prompt precisely | Aggressive — builds context before working |
| Can still find repo files via tools | Technically yes, but doesn't explore | Yes, and actively does |
| Fix | `cwd=/tmp` (already in place) | Per-run temp dir + `GEMINI.md` |

---

## Second consequence: file tool sandbox

The per-invocation temp cwd has a second effect that is not immediately
obvious: **Gemini's file tools (both read and write) are sandboxed to the
cwd**. Claude's file tools work with absolute paths regardless of cwd. Gemini's
do not.

### Read tool

If the TESTER prompt contains a path like
`/Users/david/.../user-service-target/tasks/.../store/README.md` and TESTER
tries to open it via the file read tool, Gemini rejects it:

```
I cannot access the specified job document because it is outside the
permitted workspace directory.
```

TESTER emits `TESTER_NEED_HELP` and the pipeline halts.

**Fix:** The orchestrator extracts the relevant section (`## Test Command`)
from the job doc in Python and inlines it directly into the TESTER prompt.
TESTER never needs to call the file read tool. See
`learning/pipeline-extract-dont-delegate.md`.

### Write tool

If IMPLEMENTOR tries to write a generated file to the output directory
(`/Users/david/.../user-service-output/handlers/handlers.go`) using the
`write_file` tool, Gemini rejects it:

```
Error executing tool write_file: Path not in workspace: Attempted path
".../user-service-output/handlers/handlers.go" resolves outside the allowed
workspace directories: /tmp/ai-builder-gemini-cv5447e5
```

Discovered during user-service TM regression Run 3 (2026-03-24). The first
IMPLEMENTOR in that run succeeded because the `gemini_compat.py` heredoc
addendum had prompted it to use `printf` via `run_shell_command`. The second
IMPLEMENTOR fell back to `write_file` on at least one file.

**Fix:** `gemini_compat.py` explicitly prohibits the `write_file` tool for
IMPLEMENTOR and mandates `run_shell_command` with `printf` for all file
writes. Shell commands are not subject to the cwd sandbox.

### Why shell commands are not sandboxed

`run_shell_command` spawns a shell process that inherits the environment but
is not restricted to the cwd. It can read from and write to any absolute path
the OS permits. This is the reliable escape hatch for Gemini file I/O outside
the temp cwd.

### Summary of file tool behaviour

| Operation | Claude | Gemini file tool | Gemini shell command |
|---|---|---|---|
| Read absolute path outside cwd | ✓ Works | ✗ Rejected | ✓ Works (`cat`) |
| Write absolute path outside cwd | ✓ Works | ✗ Rejected | ✓ Works (`printf`) |
