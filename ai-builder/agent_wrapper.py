import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AgentResult:
    exit_code: int   # 0=success, 1=agent error, 2=timeout
    response: str    # full text response from the agent


def run_agent(agent: str, timeout_minutes: int, role: str, prompt: str, output_dir: Path) -> AgentResult:
    """
    Run a coding agent CLI non-interactively with stream-json output.

    Streams text tokens to the terminal in real time.
    Appends raw events to execution.log inside output_dir.
    The agent subprocess runs with output_dir as its working directory so
    relative paths in generated files resolve correctly.
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

    try:
        process = subprocess.Popen(
            _build_command(agent, prompt),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=output_dir,
            env=env,
        )

        response_text = []

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

                text = _extract_text(event)
                if text:
                    response_text.append(text)
                    print(text, end="", flush=True)

        process.wait(timeout=timeout_minutes * 60)
        print()

        if process.returncode != 0:
            stderr_output = process.stderr.read()
            print(f"[agent_wrapper] {role}/{agent} exited with error (status {process.returncode})")
            if stderr_output:
                print(f"[agent_wrapper] stderr: {stderr_output.strip()}")
            return AgentResult(exit_code=1, response="".join(response_text))

        return AgentResult(exit_code=0, response="".join(response_text))

    except subprocess.TimeoutExpired:
        process.kill()
        print(f"\n[agent_wrapper] {role}/{agent} timed out after {timeout_minutes}m")
        return AgentResult(exit_code=2, response="")


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
    if event_type == "message" and event.get("role") == "assistant":
        # gemini CLI stream-json: delta message events
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
