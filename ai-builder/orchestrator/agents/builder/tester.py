import json
import subprocess
from pathlib import Path

from agent_wrapper import AgentResult


class TesterAgent:
    """Internal agent: runs the test_command from task.json."""

    def run(self, job_doc: Path, output_dir: Path, **kwargs) -> AgentResult:
        task_json_path = job_doc.parent / "task.json"
        if not task_json_path.exists():
            return AgentResult(exit_code=1, response="OUTCOME: TESTER_NEED_HELP\nHANDOFF: task.json not found; cannot determine test command.")
        try:
            tj = json.loads(task_json_path.read_text())
        except Exception as e:
            return AgentResult(exit_code=1, response=f"OUTCOME: TESTER_NEED_HELP\nHANDOFF: Failed to read task.json: {e}")

        test_command = tj.get("test_command", "").strip()
        if not test_command:
            return AgentResult(exit_code=1, response="OUTCOME: TESTER_NEED_HELP\nHANDOFF: test_command field missing from task.json.")

        try:
            proc = subprocess.run(test_command, shell=True, capture_output=True, text=True)
        except Exception as e:
            return AgentResult(exit_code=1, response=f"OUTCOME: TESTER_NEED_HELP\nHANDOFF: subprocess.run() raised an exception: {e}")

        if proc.returncode == 0:
            response = "OUTCOME: TESTER_TESTS_PASS\nHANDOFF: All tests passed."
        else:
            response = (
                f"OUTCOME: TESTER_TESTS_FAIL\n"
                f"HANDOFF: Tests failed (exit code {proc.returncode}).\n"
                f"{proc.stdout}\n{proc.stderr}"
            ).rstrip()
        return AgentResult(exit_code=0, response=response)
