import subprocess
from pathlib import Path

from agent_wrapper import AgentResult
from agents.context import AgentContext


class LCHAgent:
    """Internal agent: runs on-task-complete.sh and maps its output to outcomes."""

    def __init__(self, ctx: AgentContext) -> None:
        self.ctx = ctx

    def run(self, job_doc: Path, output_dir: Path, **kwargs) -> AgentResult:
        current_job_path = self.ctx.current_job_file.read_text().strip()
        cmd = [
            str(self.ctx.pm_scripts_dir / "on-task-complete.sh"),
            "--current", current_job_path,
            "--output-dir", str(self.ctx.run_dir),
            "--epic", self.ctx.epic,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        stdout = proc.stdout.strip()

        if proc.returncode != 0:
            err = proc.stderr.strip() or stdout
            print(f"[internal/LCH] on-task-complete.sh failed (exit {proc.returncode}): {err}")
            return AgentResult(exit_code=1, response=f"on-task-complete.sh failed: {err}")

        outcome = None
        token_line = ""
        top_rename_pending = None
        for line in proc.stdout.splitlines():
            line = line.strip()
            if line.startswith("TOP_RENAME_PENDING "):
                top_rename_pending = line[len("TOP_RENAME_PENDING "):].strip()
            elif line.startswith("NEXT "):
                outcome = "HANDLER_SUBTASKS_READY"
                token_line = line
            elif line == "DONE":
                outcome = "HANDLER_ALL_DONE"
                token_line = line
            elif line == "STOP_AFTER":
                outcome = "HANDLER_STOP_AFTER"
                token_line = line

        if outcome is None:
            print(f"[internal/LCH] unexpected output from on-task-complete.sh: {stdout!r}")
            return AgentResult(exit_code=1, response=f"Unexpected output: {stdout}")

        response = f"OUTCOME: {outcome}\nHANDOFF: ran on-task-complete.sh → {token_line}"
        if top_rename_pending:
            response += f"\nTOP_RENAME_PENDING: {top_rename_pending}"
        return AgentResult(exit_code=0, response=response)
