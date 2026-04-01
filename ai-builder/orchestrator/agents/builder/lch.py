import json
import subprocess
from pathlib import Path

from agent_wrapper import AgentResult
from agents.context import AgentContext


class LCHAgent:
    """Internal agent: runs on-task-complete.sh and maps its output to outcomes.

    Optional route_on config (from machine JSON) allows emitting different outcome
    tokens based on a field in the next task's task.json:

        "route_on": {
            "field": "component_type",
            "default": "HANDLER_SUBTASKS_READY",
            "integrate": "HANDLER_INTEGRATE_READY"
        }

    When the next task's task.json has component_type=integrate, emits
    HANDLER_INTEGRATE_READY instead of the default HANDLER_SUBTASKS_READY.
    If route_on is absent, always emits HANDLER_SUBTASKS_READY.
    """

    def __init__(self, ctx: AgentContext, route_on: dict | None = None) -> None:
        self.ctx = ctx
        self.route_on = route_on

    def _resolve_next_outcome(self, next_readme_path: str) -> str:
        """Return the outcome token for the next task, applying route_on if configured."""
        if not self.route_on:
            return "HANDLER_SUBTASKS_READY"

        field = self.route_on.get("field")
        default = self.route_on.get("default")
        if not field or not default:
            print("[internal/LCH] route_on config missing required 'field' or 'default' key")
            return "HANDLER_SUBTASKS_READY"

        task_json = Path(next_readme_path).parent / "task.json"
        if task_json.exists():
            try:
                data = json.loads(task_json.read_text())
                value = data.get(field)
                if value and value in self.route_on:
                    return self.route_on[value]
            except Exception as e:
                print(f"[internal/LCH] failed to read {task_json}: {e}")

        return default

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
                next_path = line[len("NEXT "):].strip()
                outcome = self._resolve_next_outcome(next_path)
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
