import json
import re
import subprocess
from pathlib import Path

from agent_wrapper import AgentResult
from agents.context import AgentContext


class DecomposeAgent:
    """Internal agent: creates pipeline subtasks from ARCHITECT's components list."""

    def __init__(self, ctx: AgentContext) -> None:
        self.ctx = ctx

    def run(self, job_doc: Path, output_dir: Path, **kwargs) -> AgentResult:
        components: list[dict] = kwargs.get("components") or []

        parent_dir = job_doc.parent
        task_json_path = parent_dir / "task.json"
        if not task_json_path.exists():
            return AgentResult(exit_code=1, response=f"task.json not found at {task_json_path}")

        try:
            parent_data = json.loads(task_json_path.read_text())
        except Exception as e:
            return AgentResult(exit_code=1, response=f"Failed to parse task.json: {e}")

        parent_level = parent_data.get("level", "TOP")
        parent_depth = parent_data.get("depth", 0)
        child_depth  = parent_depth + 1
        parent_output_dir = Path(parent_data.get("output_dir", str(self.ctx.output_dir)))

        if not components:
            return AgentResult(exit_code=1, response="No components provided to DECOMPOSE_HANDLER")

        in_progress_dir = self.ctx.target_repo / "project" / "tasks" / self.ctx.epic / "in-progress"
        try:
            parent_rel = str(parent_dir.relative_to(in_progress_dir))
        except ValueError:
            return AgentResult(exit_code=1, response=f"Cannot compute parent rel path: {parent_dir}")

        parent_content = job_doc.read_text()
        goal_match = re.search(r'## Goal\s*\n\n(.*?)(?=\n## |\Z)', parent_content, re.DOTALL)
        parent_goal = goal_match.group(1).strip() if goal_match else ""
        context_match = re.search(r'## Context\s*\n\n(.*?)(?=\n## |\Z)', parent_content, re.DOTALL)
        parent_context = context_match.group(1).strip() if context_match else ""
        if parent_context == "_To be written._":
            parent_context = ""

        parent_task_name = parent_dir.name
        new_level_entry = f"### Level {child_depth} — {parent_task_name}\n{parent_goal}"

        if parent_context:
            child_context = f"{parent_context}\n\n{new_level_entry}"
        else:
            child_context = new_level_entry

        subtask_dirs = []
        for i, component in enumerate(components):
            comp_name   = component["name"]
            complexity  = component["complexity"]
            description = component["description"]

            cmd = [
                str(self.ctx.pm_scripts_dir / "new-pipeline-subtask.sh"),
                "--epic", self.ctx.epic,
                "--folder", "in-progress",
                "--parent", parent_rel,
                "--name", comp_name,
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode != 0:
                err = proc.stderr.strip() or proc.stdout.strip()
                return AgentResult(exit_code=1, response=f"new-pipeline-subtask.sh failed for '{comp_name}': {err}")

            created_rel = None
            for line in proc.stdout.splitlines():
                if line.startswith("Created pipeline-subtask:"):
                    created_rel = line.split(": ", 1)[1].strip().rstrip("/")
                    break
            if created_rel is None:
                return AgentResult(exit_code=1, response=f"Cannot parse subtask path from: {proc.stdout!r}")

            subtask_dir = self.ctx.target_repo / created_rel
            subtask_dirs.append(subtask_dir)

            source_dir = component.get("source_dir", "").strip()
            if comp_name == "integrate" or not source_dir or source_dir == ".":
                comp_output_dir = parent_output_dir
            else:
                comp_output_dir = parent_output_dir / source_dir
                comp_output_dir.mkdir(parents=True, exist_ok=True)
                placeholder = comp_output_dir / "README.md"
                if not placeholder.exists():
                    placeholder.write_text(f"# {comp_name}\n\n_Placeholder. ARCHITECT fills in documentation._\n")

            subtask_json = subtask_dir / "task.json"
            if subtask_json.exists():
                try:
                    subtask_data = json.loads(subtask_json.read_text())
                    subtask_data["name"]       = comp_name
                    subtask_data["complexity"] = complexity
                    subtask_data["depth"]      = child_depth
                    subtask_data["goal"]       = description
                    subtask_data["context"]    = child_context
                    subtask_data["output_dir"] = str(comp_output_dir)
                    if comp_name == "integrate":
                        subtask_data["component_type"] = "integrate"
                    if i == len(components) - 1:
                        subtask_data["last-task"] = True
                        # Do NOT propagate parent_level to children. level=TOP must
                        # remain exclusive to the build-N entry point so that
                        # _find_level_top correctly identifies the root task when
                        # resuming from a mid-tree job doc.
                    subtask_json.write_text(json.dumps(subtask_data, indent=2) + "\n")
                except Exception as e:
                    return AgentResult(exit_code=1, response=f"Failed to update subtask task.json for '{comp_name}': {e}")

            subtask_readme = subtask_dir / "README.md"
            if subtask_readme.exists():
                readme = subtask_readme.read_text()
                readme = readme.replace(
                    "## Goal\n\n_To be written._",
                    f"## Goal\n\n{description}",
                )
                readme = readme.replace(
                    "## Context\n\n_To be written._",
                    f"## Context\n\n{child_context}",
                )
                subtask_readme.write_text(readme)

        if not subtask_dirs:
            return AgentResult(exit_code=1, response="No subtasks created")

        cmd = [
            str(self.ctx.pm_scripts_dir / "set-current-job.sh"),
            "--output-dir", str(self.ctx.run_dir),
            str(subtask_dirs[0] / "README.md"),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            err = proc.stderr.strip() or proc.stdout.strip()
            return AgentResult(exit_code=1, response=f"set-current-job.sh failed: {err}")

        if parent_data.get("stop-after"):
            response = (
                f"OUTCOME: HANDLER_STOP_AFTER\n"
                f"HANDOFF: decomposed into {len(components)} components "
                f"(level={parent_level}), first: {subtask_dirs[0].name}; "
                f"stop-after=true on parent task — pausing"
            )
            return AgentResult(exit_code=0, response=response)

        response = (
            f"OUTCOME: HANDLER_SUBTASKS_READY\n"
            f"HANDOFF: decomposed into {len(components)} components "
            f"(level={parent_level}), first: {subtask_dirs[0].name}"
        )
        return AgentResult(exit_code=0, response=response)
