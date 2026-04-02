"""
Render a README.md for a pipeline task from its task.json.

task.json is authoritative; README.md is a generated view — never written
directly by pipeline agents.

Two modes depending on the task's level field:
  - TOP-level task: full view — run summary, execution log, subtask list
  - Non-TOP task:   subtask list only

Usage (CLI):
    python3 render_readme.py --task path/to/task.json

Usage (in-process):
    from render_readme import render_task_readme
    render_task_readme(task_json_path)   # writes README.md alongside task.json
"""

import argparse
import json
from datetime import timedelta
from pathlib import Path


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def render_task_readme(task_json_path: Path) -> None:
    """Read task.json and write README.md alongside it."""
    try:
        data = json.loads(task_json_path.read_text())
    except Exception:
        return

    level = data.get("level", "")
    if level == "TOP":
        content = _render_top(data)
    else:
        content = _render_subtask(data)

    readme_path = task_json_path.parent / "README.md"
    readme_path.write_text(content)


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------

def _render_top(data: dict) -> str:
    # Prefer parent (e.g. "50faa0-platform") as the title; fall back to goal first line
    title = data.get("parent") or data.get("name") or ""
    if not title:
        goal = data.get("goal", "Pipeline Task")
        title = goal.splitlines()[0].strip() if goal else "Pipeline Task"

    lines = [f"# {title}", ""]

    # Run summary (only if present)
    summary = data.get("run_summary")
    if summary:
        lines += _render_run_summary(summary)

    # Execution log
    execution_log = data.get("execution_log", [])
    if execution_log:
        lines += _render_execution_log(execution_log)

    # Subtask list
    subtasks = data.get("subtasks", [])
    if subtasks:
        lines += _render_subtask_list(subtasks)

    return "\n".join(lines) + "\n"


def _render_subtask(data: dict) -> str:
    name = data.get("name", data.get("goal", "Subtask"))
    title = name.splitlines()[0].strip() if name else "Subtask"

    lines = [f"# {title}", ""]

    # Goal — always present for pipeline subtasks (set by decompose.py)
    goal = data.get("goal", "")
    if goal:
        lines += ["## Goal", "", goal, ""]

    # Context — breadcrumb trail set by decompose.py
    context = data.get("context", "")
    if context:
        lines += ["## Context", "", context, ""]

    # Design — written by ARCHITECT on design-ready outcome; already has "## Design" header
    design = data.get("design", "")
    if design:
        lines += [design, ""]

    # Acceptance Criteria — written by ARCHITECT; already has "## Acceptance Criteria" header
    ac = data.get("acceptance_criteria", "")
    if ac:
        lines += [ac, ""]

    # Test Command — written by ARCHITECT
    tc = data.get("test_command", "")
    if tc:
        lines += ["## Test Command", "", "```", tc, "```", ""]

    # Subtask list (composite nodes only)
    subtasks = data.get("subtasks", [])
    if subtasks:
        lines += _render_subtask_list(subtasks)

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def _render_run_summary(summary: dict) -> list[str]:
    start   = summary.get("start", "—")
    end     = summary.get("end", "—")
    elapsed = _fmt_elapsed_s(summary.get("elapsed_s", 0))
    t_in    = summary.get("total_tokens_in", 0)
    t_out   = summary.get("total_tokens_out", 0)
    t_cache = summary.get("total_tokens_cached", 0)
    n_inv   = summary.get("invocation_count", 0)

    return [
        "## Run Summary",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| Start | {start} |",
        f"| End | {end} |",
        f"| Elapsed | {elapsed} |",
        f"| Invocations | {n_inv} |",
        f"| Tokens in | {t_in:,} |",
        f"| Tokens out | {t_out:,} |",
        f"| Tokens cached | {t_cache:,} |",
        "",
    ]


def _render_execution_log(log: list[dict]) -> list[str]:
    lines = [
        "## Execution Log",
        "",
        "| # | Role | Agent | Description | Outcome | Elapsed | Tokens In | Tokens Out | Tokens Cached |",
        "|---|------|-------|-------------|---------|---------|-----------|------------|---------------|",
    ]
    for i, inv in enumerate(log, 1):
        elapsed = _fmt_elapsed_s(inv.get("elapsed_s", 0))
        lines.append(
            f"| {i} | {inv.get('role', '—')} | {inv.get('agent', '—')} "
            f"| {inv.get('description', '—')} | {inv.get('outcome', '—')} "
            f"| {elapsed} | {inv.get('tokens_in', 0):,} "
            f"| {inv.get('tokens_out', 0):,} | {inv.get('tokens_cached', 0):,} |"
        )
    lines.append("")
    return lines


def _render_subtask_list(subtasks: list[dict]) -> list[str]:
    lines = ["## Subtasks", ""]
    for st in subtasks:
        done   = st.get("complete", False)
        name   = st.get("name", "—")
        marker = "x" if done else " "
        lines.append(f"- [{marker}] {name}")
    lines.append("")
    return lines


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt_elapsed_s(seconds: float) -> str:
    td = timedelta(seconds=int(seconds))
    m, s = divmod(int(td.total_seconds()), 60)
    return f"{m}m {s:02d}s" if m else f"{s}s"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _main() -> None:
    parser = argparse.ArgumentParser(description="Render README.md from task.json")
    parser.add_argument("--task", required=True, help="Path to task.json")
    args = parser.parse_args()

    task_json_path = Path(args.task)
    if not task_json_path.exists():
        print(f"Error: {task_json_path} does not exist")
        raise SystemExit(1)

    render_task_readme(task_json_path)
    print(f"Wrote {task_json_path.parent / 'README.md'}")


if __name__ == "__main__":
    _main()
