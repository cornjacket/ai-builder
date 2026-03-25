# gemini_compat.py

Purpose: Single home for all Gemini CLI prompt shims. Exports
`gemini_role_addendum(role)`, which returns a Markdown block appended to
the prompt when the orchestrator is running with `--agent gemini`. Returns
an empty string for roles that have no Gemini-specific rules.

Tags: gemini, orchestrator, compatibility, prompt-engineering

---

## Why this file exists

Gemini CLI has behavioural differences from Claude Code that cause pipeline
failures if left unaddressed. Rather than scattering workarounds across
`orchestrator.py` or the role prompt files, all Gemini-specific additions
live here. Each shim is annotated with the issue it addresses, when it was
discovered, and which bug task it belongs to.

**Usage in orchestrator.py:**
```python
from gemini_compat import gemini_role_addendum
if agent == "gemini":
    prompt += gemini_role_addendum(role)
```

---

## Known Gemini CLI Behavioural Differences

### 1. `read_file` tool is sandboxed to the temp cwd

**Symptom:** Any call to `read_file` with an absolute path outside the
agent's temp workspace directory is rejected:
```
Path not in workspace: Attempted path "..." resolves outside the allowed
workspace directories: /tmp/ai-builder-gemini-xxx
```

**Affected roles:** ARCHITECT, IMPLEMENTOR, TESTER (before fixes).

**Fix (orchestrator.py):** Extract all required job doc sections in Python
and inline them directly into each agent's prompt. The agent receives Goal,
Context, Design, Acceptance Criteria, and Test Command as prompt text and
never needs to call `read_file` for job doc content.

**Discovered:** user-service TM regression (2026-03-23 / 2026-03-24).
**Bug:** `024459-bug-gemini-agent-cannot-read-job-doc`

---

### 2. `write_file` tool is sandboxed to the temp cwd

**Symptom:** Any call to `write_file` with an absolute path outside the
agent's temp workspace directory is rejected:
```
Path not in workspace: ... resolves outside the allowed workspace directories
```

**Affected roles:** IMPLEMENTOR (source files), ARCHITECT (documentation files).
Both write to `output_dir`, which is an absolute path outside the sandbox.

**Fix (gemini_compat.py):** Inject a `## File Writing Rules` addendum for
IMPLEMENTOR and ARCHITECT prohibiting `write_file` and mandating
`run_shell_command` with `printf` instead:
```
printf '%s' 'file content here' > /absolute/path/to/filename.go
```
Shell commands executed via `run_shell_command` are not subject to the cwd
sandbox.

**Discovered:** IMPLEMENTOR: user-service regression Run 3 (2026-03-24).
ARCHITECT: user-service regression (2026-03-24).
**Bug:** `024459-bug-gemini-agent-cannot-read-job-doc`

---

### 3. Heredoc syntax causes shell parse errors

**Symptom:** `cat <<'EOF' ... EOF` heredoc syntax passed to
`run_shell_command` produces a shell parse error before the command runs.

**Affected roles:** IMPLEMENTOR (primary), ARCHITECT (secondary).

**Fix (gemini_compat.py):** Same `## File Writing Rules` addendum as above
explicitly prohibits heredoc syntax and mandates `printf '%s' '...' > file`.

**Discovered:** user-service TM regression Run 1 (2026-03-23).
**Model affected:** gemini-3-flash-preview.
**Bug:** `024459-bug-gemini-agent-cannot-read-job-doc`

---

### 4. TESTER runs from a temp cwd with no Go module

**Symptom:** TESTER runs `go test ./...` from its temp sandbox cwd, which
contains no Go module, causing `go test` to fail with:
```
pattern ./...: directory prefix . does not contain main module
```

**Fix (orchestrator.py):** Prepend `cd <output_dir> && ` to the inlined
test command so the command is fully self-contained. TESTER receives a
complete, runnable command and requires no working-directory reasoning.

**Discovered:** user-service regression (2026-03-24).
**Bug:** `024459-bug-gemini-agent-cannot-read-job-doc` (subtask 0004)

---

### 5. Gemini explores extensively before working

**Symptom:** Gemini agents spend 5–10 tool calls exploring the filesystem
(listing directories, checking environment variables, reading unrelated files)
before beginning the actual task. This is especially pronounced in ARCHITECT.

**Status:** Not fixed. Acknowledged as a behavioural difference. No prompt
shim has been found to reliably suppress it without introducing other
regressions.

**See:** `sandbox/brainstorm-claude-vs-gemini-behavioral-differences.md`

---

## Adding a new shim

1. Identify the role(s) affected.
2. Add an `if role == "ROLE_NAME":` block in `gemini_role_addendum()`.
3. Annotate the block with: what the issue is, when it was discovered,
   which model was affected, and which bug task it belongs to.
4. Update this document with a new entry under **Known Gemini CLI
   Behavioural Differences**.

Do not add Gemini workarounds anywhere else in the codebase.
