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

Token counts are captured from the `result` event in the claude CLI's stream-json
output (`event.usage.input_tokens`, `output_tokens`, `cache_read_input_tokens`).
Non-claude agents return zeros for all token fields.

---

### `run_agent(agent, timeout_minutes, role, prompt, output_dir) -> AgentResult`

| Parameter | Type | Description |
|-----------|------|-------------|
| `agent` | str | Agent name: `"claude"` or `"gemini"` |
| `timeout_minutes` | int | Hard timeout; kills subprocess and returns exit_code=2 |
| `role` | str | Role name used for log file naming and display |
| `prompt` | str | Full prompt string passed via `-p` flag |
| `output_dir` | Path | Working directory for the subprocess; log files written here |

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

The subprocess runs with `cwd=output_dir` so relative paths in agent-generated
files resolve to the correct location.

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Agent completed successfully (non-zero subprocess return code still yields 1) |
| 1 | Agent subprocess exited with non-zero status |
| 2 | Timeout: subprocess killed after `timeout_minutes` |
