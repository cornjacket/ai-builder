import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


# GEMINI.md written to a per-invocation temp dir to scope Gemini's behaviour.
# Gemini reads GEMINI.md from its cwd at startup as session configuration.
# Without this, Gemini explores absolute paths in the prompt back to the repo,
# finds CLAUDE.md, and follows Oracle instructions instead of pipeline instructions.
_GEMINI_MD = """\
You are a focused pipeline agent executing a specific role in a build pipeline.

Rules:
- Follow ONLY the instructions in your prompt. Nothing else takes priority.
- Do NOT read CLAUDE.md, GEMINI.md, or any project configuration files.
- Do NOT read session status files, task logs, or task management files.
- Do NOT explore directory structures beyond paths explicitly given in your prompt.
- Do NOT run project setup scripts, task management scripts, or shell commands
  unrelated to the task described in your prompt.
"""


@dataclass
class AgentResult:
    exit_code: int   # 0=success, 1=agent error, 2=timeout
    response: str    # full text response from the agent
    tokens_in: int = 0
    tokens_out: int = 0
    tokens_cached: int = 0


def run_agent(agent: str, timeout_minutes: int, role: str, prompt: str, output_dir: Path) -> AgentResult:
    """
    Run a coding agent CLI non-interactively with stream-json output.

    Streams text tokens to the terminal in real time.
    Appends raw events to execution.log inside output_dir.
    The agent subprocess runs with a neutral CWD to avoid loading unintended
    context from the filesystem.
    Returns the full response text alongside the exit code.
    """
    print(f"[agent_wrapper] agent={agent} role={role} timeout={timeout_minutes}m", flush=True)

    logs_dir      = output_dir / "logs"
    execution_log = output_dir / "execution.log"

    logs_dir.mkdir(parents=True, exist_ok=True)
    role_log = logs_dir / f"{role}.log"

    # Strip CLAUDECODE so the claude CLI doesn't refuse to start. Claude Code
    # sets this variable and the CLI checks for it to block nested interactive
    # sessions. Our subprocesses use -p (non-interactive) so the concern
    # doesn't apply, but the check is unconditional.
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    # Determine cwd for the subprocess.
    # Claude: /tmp — prevents CLAUDE.md from being loaded (Claude walks up from
    #   cwd at startup to find and inject CLAUDE.md files).
    # Gemini: a per-invocation temp dir containing a scoped GEMINI.md — Gemini
    #   reads GEMINI.md from cwd at startup. Without this, Gemini explores the
    #   repo via absolute paths in the prompt, finds CLAUDE.md, and follows
    #   Oracle instructions. See learning/agent-cwd-and-context-isolation.md.
    if agent == "gemini":
        agent_cwd = Path(tempfile.mkdtemp(prefix="ai-builder-gemini-"))
        (agent_cwd / "GEMINI.md").write_text(_GEMINI_MD)
    else:
        agent_cwd = Path("/tmp")

    try:
        process = subprocess.Popen(
            _build_command(agent, prompt),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=agent_cwd,
            env=env,
        )

        response_text = []
        tokens_in = tokens_out = tokens_cached = 0

        with role_log.open("w") as role_out, execution_log.open("a") as exec_out:
            for line in process.stdout:
                role_out.write(line)
                role_out.flush()
                exec_out.write(line)
                exec_out.flush()

                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    print(f"[debug] non-json line: {line.rstrip()}", flush=True)
                    continue

                print(f"[debug] event type: {event.get('type')}", flush=True)

                # Capture token usage from the final result event.
                # Claude: {"type":"result","usage":{"input_tokens":N,"output_tokens":N,"cache_read_input_tokens":N}}
                # Gemini: {"type":"result","stats":{"input":N,"output_tokens":N,"cached":N}}
                #   where "input" is non-cached input only; "input_tokens" is total (cached+non-cached).
                if event.get("type") == "result":
                    if "usage" in event:
                        usage = event["usage"]
                        tokens_in     = usage.get("input_tokens", 0)
                        tokens_out    = usage.get("output_tokens", 0)
                        tokens_cached = usage.get("cache_read_input_tokens", 0)
                    elif "stats" in event:
                        stats = event["stats"]
                        tokens_in     = stats.get("input", 0)
                        tokens_out    = stats.get("output_tokens", 0)
                        tokens_cached = stats.get("cached", 0)

                text = _extract_text(event)
                if text:
                    # If this chunk contains OUTCOME: and the previous accumulated
                    # text doesn't end with a newline, inject one. Gemini can split
                    # a delta mid-line, producing "...textOUTCOME: X" without a
                    # preceding newline, which breaks the ^OUTCOME: regex.
                    if "OUTCOME:" in text and response_text and not response_text[-1].endswith("\n"):
                        response_text.append("\n")
                    response_text.append(text)
                    print(text, end="", flush=True)

        process.wait(timeout=timeout_minutes * 60)
        print()

        if process.returncode != 0:
            stderr_output = process.stderr.read()
            print(f"[agent_wrapper] {role}/{agent} exited with error (status {process.returncode})")
            if stderr_output:
                print(f"[agent_wrapper] stderr: {stderr_output.strip()}")
            return AgentResult(exit_code=1, response="".join(response_text),
                               tokens_in=tokens_in, tokens_out=tokens_out, tokens_cached=tokens_cached)

        return AgentResult(exit_code=0, response="".join(response_text),
                           tokens_in=tokens_in, tokens_out=tokens_out, tokens_cached=tokens_cached)

    except subprocess.TimeoutExpired:
        process.kill()
        print(f"\n[agent_wrapper] {role}/{agent} timed out after {timeout_minutes}m")
        return AgentResult(exit_code=2, response="")
    finally:
        if agent == "gemini":
            shutil.rmtree(agent_cwd, ignore_errors=True)


def _extract_text(event: dict) -> str:
    event_type = event.get("type", "")
    if event_type == "content_block_delta":
        # streaming API deltas: {"type":"content_block_delta","delta":{"type":"text_delta","text":"..."}}
        delta = event.get("delta", {})
        if isinstance(delta, dict):
            return delta.get("text", "")
    if event_type == "assistant":
        # claude CLI stream-json: full message content blocks
        for block in event.get("message", {}).get("content", []):
            if isinstance(block, dict) and block.get("type") == "text":
                return block.get("text", "")
    if event_type == "message" and event.get("role") == "assistant" and event.get("delta"):
        # gemini CLI stream-json: streaming delta message events
        return event.get("content", "")
    return ""


def _resolve(agent: str) -> str:
    resolved = shutil.which(agent)
    if not resolved:
        raise FileNotFoundError(f"Agent executable not found in PATH: {agent}")
    return resolved


def _build_command(agent: str, prompt: str) -> list:
    exe = _resolve(agent)
    if agent == "claude":
        return [
            exe,
            "--output-format", "stream-json",
            "--verbose",
            "--allowedTools", "Read,Edit,Write,Bash",
            "-p", prompt,
        ]
    if agent == "gemini":
        return [
            exe,
            "--output-format", "stream-json",
            "--yolo",
            "-p", prompt,
        ]
    return [exe, "-p", prompt]
