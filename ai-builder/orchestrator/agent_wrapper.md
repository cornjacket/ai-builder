# agent_wrapper.py

Spawns agent CLI subprocesses non-interactively, streams their output in
real time, and returns a structured result to the orchestrator.

---

## Public Interface

### `AgentResult`

```python
@dataclass
class AgentResult:
    exit_code: int        # 0=success, 1=agent error, 2=timeout
    response: str         # full concatenated text response from the agent
    tokens_in: int        # input tokens (claude CLI only; 0 for other agents)
    tokens_out: int       # output tokens (claude CLI only; 0 for other agents)
    tokens_cached: int    # cache-read input tokens (claude CLI only; 0 for other agents)
```

Token counts are captured from the `result` event in each CLI's stream-json output.

| Agent | Token source | Field mapping |
|-------|-------------|---------------|
| `claude` | `event.usage` | `input_tokens` → `tokens_in`, `output_tokens` → `tokens_out`, `cache_read_input_tokens` → `tokens_cached` |
| `gemini` | `event.stats` | `input` (non-cached only) → `tokens_in`, `output_tokens` → `tokens_out`, `cached` → `tokens_cached` |

Note: Gemini's `stats.input_tokens` is total input including cached tokens. `stats.input`
is the non-cached portion only — equivalent to Claude's `usage.input_tokens`. Using
`stats.input_tokens` for `tokens_in` would inflate Gemini's input count by the cached
amount, making cross-agent comparisons misleading.

---

### `run_agent(agent, timeout_minutes, role, prompt, output_dir) -> AgentResult`

| Parameter | Type | Description |
|-----------|------|-------------|
| `agent` | str | Agent name: `"claude"` or `"gemini"` |
| `timeout_minutes` | int | Hard timeout; kills subprocess and returns exit_code=2 |
| `role` | str | Role name used for log file naming and display |
| `prompt` | str | Full prompt string passed via `-p` flag |
| `output_dir` | Path | Directory where log files are written (NOT used as subprocess cwd — see Environment) |

**Side effects:**
- Creates `output_dir/logs/` if it does not exist
- Writes raw stream-json events to `output_dir/logs/<ROLE>.log`
- Appends raw stream-json events to `output_dir/execution.log`
- Streams extracted text to stdout in real time

**Return:** `AgentResult` with `exit_code` and full `response` text.

---

## Private Functions

### `_build_command(agent, prompt) -> list`

Constructs the CLI argument list for the given agent.

| Agent | Command |
|-------|---------|
| `claude` | `claude --output-format stream-json --verbose --allowedTools Read,Edit,Write,Bash -p <prompt>` |
| `gemini` | `gemini --output-format stream-json --yolo -p <prompt>` |
| other | `<exe> -p <prompt>` |

`--allowedTools` for claude is fixed at `Read,Edit,Write,Bash`. Gemini uses
`--yolo` (unrestricted tool access).

---

### `_resolve(agent) -> str`

Resolves the agent name to a full executable path using `shutil.which()`.
Raises `FileNotFoundError` if not found in PATH. This is necessary because
nvm-managed executables may not be on the PATH inherited by Python subprocesses
when the orchestrator is invoked from certain environments.

---

### `_extract_text(event) -> str`

Extracts human-readable text from a single stream-json event. Handles three
event formats:

| Format | Event type | Text location |
|--------|-----------|---------------|
| Claude API streaming | `content_block_delta` | `event.delta.text` |
| Claude CLI stream-json | `assistant` | `event.message.content[].text` |
| Gemini CLI stream-json | `message` (role=assistant) | `event.content` |

Returns empty string for non-text events (tool use, system, etc.).

---

## Environment

The subprocess inherits `os.environ` with `CLAUDECODE` removed. This variable
is set by Claude Code and the claude CLI checks for it unconditionally to
block nested interactive sessions. Subprocesses use `-p` (non-interactive)
so blocking is unnecessary, but the check is unconditional in the CLI.

**Claude:** The subprocess runs with `cwd=/tmp`. The Claude CLI walks upward from
cwd at startup to find and inject `CLAUDE.md` files into the agent's context. With
`cwd=/tmp`, the walk reaches `/` without finding any `CLAUDE.md` — the developer
`CLAUDE.md` in the ai-builder repo is never loaded. All context the agent needs is
injected explicitly through the prompt; cwd is irrelevant for file I/O because all
paths in prompts are absolute.

**Gemini:** `cwd=/tmp` prevents `GEMINI.md` from being auto-loaded at startup, but
Gemini is significantly more exploratory than Claude at runtime. When the prompt
contains an absolute path to a file inside the repo, Gemini will actively traverse
the repo directory structure, find `CLAUDE.md`, and treat it as authoritative
session context — causing it to follow Oracle-level instructions (status file reads,
task decomposition conventions) instead of pipeline agent instructions. The correct
fix for Gemini is a per-invocation temp directory with a `GEMINI.md` that scopes
Gemini's behaviour to the pipeline task. See
[learning/agent-cwd-and-context-isolation.md](../../../learning/agent-cwd-and-context-isolation.md)
for the full analysis.

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Agent completed successfully (non-zero subprocess return code still yields 1) |
| 1 | Agent subprocess exited with non-zero status |
| 2 | Timeout: subprocess killed after `timeout_minutes` |
