# Brainstorm: Claude Code vs Gemini CLI Behavioral Differences

Empirical findings from running both agents as pipeline subprocesses in
ai-builder. Each section describes the difference, how it was discovered,
and how it is resolved (or what resolution is pending).

---

## 1. File Tools (read and write) — cwd Sandboxing

### Difference

**Claude Code:** The file read and write tools work with absolute paths
regardless of the current working directory. Running Claude with `cwd=/tmp`
does not prevent it from reading or writing files at absolute paths elsewhere.

**Gemini CLI:** Both the file read tool and the `write_file` tool are sandboxed
to the cwd. If Gemini is launched with `cwd=/tmp/ai-builder-gemini-xyz`, any
attempt to access a file at an absolute path outside that directory is rejected:

```
# read tool:
I cannot access the specified job document because it is outside the
permitted workspace directory.

# write_file tool:
Error executing tool write_file: Path not in workspace: Attempted path
".../sandbox/user-service-output/handlers/handlers.go" resolves outside
the allowed workspace directories: /tmp/ai-builder-gemini-cv5447e5
```

Shell commands (`run_shell_command`) are **not** subject to this sandbox —
they can access any absolute path.

### Discovery

- **Read tool:** user-service TM regression Run 2 (2026-03-23). TESTER tried
  to read the job doc via the file tool and emitted `TESTER_NEED_HELP`.
- **Write tool:** user-service TM regression Run 3 (2026-03-24). Second
  IMPLEMENTOR invocation attempted `write_file` for `handlers/handlers.go`
  and was rejected. First IMPLEMENTOR had succeeded using `printf` via
  `run_shell_command` (prompted by the heredoc fix addendum).

### Resolution

**Read tool (implemented):** Orchestrator extracts relevant job doc sections
and inlines them into the prompt. TESTER receives `## Test Command` inline;
no file read needed. See `learning/pipeline-extract-dont-delegate.md`.

**Write tool (implemented):** `gemini_compat.py` addendum for IMPLEMENTOR
explicitly prohibits `write_file` and mandates `run_shell_command` with
`printf` for all file writes:

```
Always write files using run_shell_command with printf — NOT the write_file
tool and NOT heredocs:
  printf '%s' 'file content here' > /absolute/path/to/filename.go
```

---

## 2. CLAUDE.md / GEMINI.md Auto-Loading

### Difference

**Claude Code:** At startup, Claude Code walks up the directory tree from its
cwd, finding and loading every `CLAUDE.md` it encounters. Running with
`cwd=/tmp` means the walk finds nothing — no project config is injected. This
is a reliable isolation mechanism.

**Gemini CLI:** Gemini does not walk up from the cwd. Instead, when given a
prompt containing absolute paths (e.g. the target repo), Gemini explores the
filesystem via those paths and finds `GEMINI.md` (or `CLAUDE.md`) files. Setting
`cwd=/tmp` does nothing — Gemini follows absolute paths in the prompt back to
the repo and loads the config files it finds there.

During early testing, Gemini loaded ai-builder's `CLAUDE.md` (9K bytes),
modified the job document, and produced `ARCHITECT_DECOMPOSITION_READY` for
an atomic task — contaminating the run.

### Discovery

First Gemini fibonacci regression (2026-03-23). Confirmed by observing token
input drop from ~21K to ~7K after the fix (GEMINI.md loaded, ai-builder
CLAUDE.md not loaded).

### Resolution (implemented)

Per-invocation temp directory with a scoped `GEMINI.md`:

```python
agent_cwd = Path(tempfile.mkdtemp(prefix="ai-builder-gemini-"))
(agent_cwd / "GEMINI.md").write_text(_GEMINI_MD)
```

The `_GEMINI_MD` content scopes Gemini to pipeline-agent behaviour:
- Follow only the prompt
- Do not read CLAUDE.md, GEMINI.md, or project config files
- Do not explore directory structures beyond paths in the prompt
- Do not run task management scripts

The temp dir is cleaned up in a `finally` block after the invocation.

**Reference:** `learning/agent-cwd-and-context-isolation.md`

---

## 3. Heredoc Syntax — Shell Parse Errors

### Difference

**Claude Code:** Handles heredoc syntax in shell commands without issue.
Multi-line file writes using `cat <<'EOF' > file.go ... EOF` work correctly.

**Gemini CLI:** Gemini's tool execution layer misinterprets heredoc syntax,
producing parse errors before the command runs:

```
'Error node: "<" at 0:0'
'Missing node: "" at 9:22'
```

### Discovery

User-service TM regression Run 1 (2026-03-23). The IMPLEMENTOR for the `store`
component attempted heredoc-style file writes. The model responsible was
`gemini-3-flash-preview` (confirmed via `stats.models` in the result event —
248K input tokens, 10K output, 20 tool calls).

Notably, in Run 2 (the immediately following run), Gemini proactively used
`printf` instead of heredocs — but only because the failed run's handoff was
still in the session context. A cold start will not retain this behaviour.

### Resolution (pending)

Add an explicit prohibition to the Gemini-specific IMPLEMENTOR prompt
(e.g. `roles/IMPLEMENTOR-gemini.md` referenced in the Gemini machine JSONs):

```
When writing multi-line files, use printf rather than heredocs:
  printf '%s' "content" > file.go
Do NOT use cat <<'EOF' ... EOF syntax — it causes parse errors.
```

This makes the rule permanent and deterministic rather than session-dependent.

---

## 4. Stream-JSON Event Format

### Difference

**Claude Code** (`--output-format stream-json`):
- Text output: `{"type":"assistant","message":{"content":[{"type":"text","text":"..."}]}}`
- Token usage: `{"type":"result","usage":{"input_tokens":N,"output_tokens":N,"cache_read_input_tokens":N}}`

**Gemini CLI** (`--output-format stream-json`):
- Text output: `{"type":"message","role":"assistant","delta":true,"content":"..."}` (streaming deltas, may split mid-word)
- Token usage: `{"type":"result","stats":{"input":N,"output_tokens":N,"cached":N,"models":{...}}}`

Key field name differences:
- Claude: `usage.input_tokens` (total incl. cached), `usage.cache_read_input_tokens`
- Gemini: `stats.input` (non-cached only), `stats.cached`, `stats.input_tokens` (total)

Using the wrong field gives incorrect token counts. Early implementation
mistakenly used `stats.input_tokens` (total) instead of `stats.input`
(non-cached), making tokens_in appear inflated.

### Discovery

Gemini stream-json format investigation (sandbox/gemini-experiments/),
confirmed during token tracking implementation (e62647-0001).

### Resolution (implemented)

`agent_wrapper.py` branches on event key:

```python
if "usage" in event:      # Claude
    tokens_in     = usage.get("input_tokens", 0)
    tokens_cached = usage.get("cache_read_input_tokens", 0)
elif "stats" in event:    # Gemini
    tokens_in     = stats.get("input", 0)       # non-cached only
    tokens_cached = stats.get("cached", 0)
```

---

## 5. OUTCOME: Line Splitting (Delta Streaming)

### Difference

**Claude Code:** Text output arrives in complete chunks; `OUTCOME:` always
appears at the start of a line. The regex `^OUTCOME:` reliably matches.

**Gemini CLI:** Text output arrives as streaming deltas that can split
anywhere — including mid-line, mid-word. A delta containing `\nOUTCOME:` may
arrive split as `\nOUTCO` + `ME: DONE`, causing the regex to fail and the
outcome to go undetected.

### Resolution (implemented)

`agent_wrapper.py` injects a newline before any text chunk containing
`OUTCOME:` before appending to the accumulation buffer, ensuring the regex
always has a newline prefix to match against:

```python
if "OUTCOME:" in text:
    full_text += "\n"
full_text += text
```

---

## 6. Per-Turn Model Routing

### Difference

**Claude Code:** One model for the entire invocation. `--model` is a hard pin.

**Gemini CLI:** Default mode (`auto-gemini-3`) routes each turn to a different
model based on perceived complexity. Observed routing:
- `gemini-2.5-flash-lite` — simple turns (short responses, quick tool calls)
- `gemini-3-flash-preview` — heavy reasoning turns

Per-model token breakdown is available in `stats.models` in the result event.
You cannot predict or control which model handles a given turn in auto mode.

### Discovery / Resolution

Documented in `learning/agent-model-selection.md`. The `4f9fba-add-model-selection-to-machine-config` task adds a `"model"` field to machine JSON role configs to allow pinning a specific model per role.

---

## 7. CLI Flags

### Difference

| Flag | Claude | Gemini |
|------|--------|--------|
| Suppress confirmation prompts | (not needed) | `--yolo` required |
| Output format | `--output-format stream-json` | `--output-format stream-json` |
| Model selection | `--model <id>` | `--model <id>` |

Gemini without `--yolo` pauses for user confirmation on tool calls, which
hangs the pipeline.

### Resolution (implemented)

`_build_command` in `agent_wrapper.py` appends `--yolo` for Gemini invocations.

---

## Summary Table

| Difference | Claude | Gemini | Status |
|---|---|---|---|
| File read tool cwd sandboxing | Absolute paths work | Sandboxed to cwd | Fixed (inline content in prompts via orchestrator) |
| File write tool cwd sandboxing | Absolute paths work | Sandboxed to cwd | Fixed (gemini_compat.py — prohibit write_file, use printf) |
| Config file auto-loading | Walks up from cwd | Follows absolute paths in prompt | Fixed (per-invocation GEMINI.md temp dir) |
| Heredoc shell syntax | Works | Parse errors | Fixed (gemini_compat.py — prohibit heredocs, use printf) |
| Stream-json event format | `usage` key | `stats` key | Fixed (branch in agent_wrapper.py) |
| OUTCOME: line splitting | Clean lines | May split mid-line | Fixed (newline injection) |
| Per-turn model routing | Single model | Auto-routes per turn | Tracked in 4f9fba |
| CLI flags | Standard | Requires `--yolo` | Fixed |
