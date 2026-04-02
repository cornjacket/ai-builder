"""
Pipeline build metrics — capture, live update, and end-of-run reporting.

The orchestrator calls these functions after each agent invocation and on
pipeline completion. Agents are entirely unaware of this module.

These functions are the seam for future persistence (database, dashboard):
replace or wrap them without touching orchestrator.py.
"""

import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class InvocationRecord:
    role: str
    agent: str          # CLI agent name, e.g. "claude", "gemini"
    n: int              # per-role invocation count (1-based)
    description: str    # human-readable task name derived from job path
    start: datetime
    end: datetime
    elapsed: timedelta
    tokens_in: int
    tokens_out: int
    tokens_cached: int
    outcome: str


@dataclass
class RunData:
    task_name: str
    start: datetime
    invocations: list[InvocationRecord] = field(default_factory=list)
    end: datetime | None = None
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def record_invocation(
    run: RunData,
    role: str,
    agent: str,
    role_counter: int,
    description: str,
    start: datetime,
    end: datetime,
    tokens_in: int,
    tokens_out: int,
    tokens_cached: int,
    outcome: str,
) -> InvocationRecord:
    """Create an InvocationRecord and append it to run.invocations."""
    inv = InvocationRecord(
        role=role,
        agent=agent,
        n=role_counter,
        description=description,
        start=start,
        end=end,
        elapsed=end - start,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        tokens_cached=tokens_cached,
        outcome=outcome,
    )
    run.invocations.append(inv)
    return inv


def description_from_job_path(job_path: Path | None) -> str:
    """Derive a human-readable description from a job document path.

    Strips the leading '{id}-{NNNN}-' or '{id}-' prefix from the directory
    name, e.g.:
      eab6f7-0001-handler/README.md  → 'handler'
      fa3480-build-1/README.md       → 'build-1'
      eab6f7-user-service/README.md  → 'user-service'
    """
    if job_path is None:
        return "—"
    name = job_path.parent.name
    # Strip {6-hex}-{4-digit}- prefix (incremental subtask IDs)
    m = re.match(r'^[0-9a-f]{6}-\d{4}-(.+)$', name)
    if m:
        return m.group(1)
    # Strip {6-hex}- prefix (top-level task IDs)
    m = re.match(r'^[0-9a-f]{6}-(.+)$', name)
    if m:
        return m.group(1)
    return name


def update_task_doc(build_readme: Path, run: RunData) -> None:
    """Rewrite (or insert) the ## Execution Log section of the Level:TOP pipeline-subtask README.

    If the section already exists, replaces it in place.
    If not, inserts it after the ## Goal section.
    """
    if not build_readme.exists():
        return

    content = build_readme.read_text()
    section_header = "## Execution Log"
    if section_header not in content:
        # Insert after ## Goal section (before the next ## heading)
        goal_match = re.search(r'(## Goal\n.*?)(\n## )', content, re.DOTALL)
        if not goal_match:
            return
        insert_pos = goal_match.start(2)
        content = content[:insert_pos] + f"\n{section_header}\n\n| # | Role | Agent | Description | Ended | Elapsed | Tokens In | Tokens Out | Tokens Cached |\n|---|------|-------|-------------|-------|---------|-----------|------------|---------------|\n" + content[insert_pos:]

    # Build replacement rows
    rows = []
    for i, inv in enumerate(run.invocations, 1):
        elapsed = _fmt_elapsed(inv.elapsed)
        ended   = inv.end.strftime("%H:%M:%S")
        rows.append(
            f"| {i} | {inv.role} | {inv.agent} | {inv.description} "
            f"| {ended} | {elapsed} "
            f"| {inv.tokens_in:,} | {inv.tokens_out:,} | {inv.tokens_cached:,} |"
        )

    table_header = (
        "| # | Role | Agent | Description | Ended | Elapsed "
        "| Tokens In | Tokens Out | Tokens Cached |"
    )
    table_sep = "|---|------|-------|-------------|-------|---------|-----------|------------|---------------|"
    new_section = "\n".join([section_header, "", table_header, table_sep] + rows)

    # Replace the ## Execution Log section only — stop at the next ## heading
    # so that Design, Acceptance Criteria, etc. are preserved.
    new_content = re.sub(
        r'## Execution Log(?:\n(?!## ).*)*',
        new_section + "\n",
        content,
    )
    build_readme.write_text(new_content)


def write_metrics_to_task_json(task_json_path: Path | None, run: RunData, final: bool = False) -> None:
    """Write execution_log (and run_summary if final) to task.json.

    Called after each invocation to accumulate the execution log, and once
    more at pipeline completion with final=True to write the run_summary totals.
    """
    if task_json_path is None or not task_json_path.exists():
        return
    try:
        tj = json.loads(task_json_path.read_text())
    except Exception:
        return

    tj["execution_log"] = [_inv_dict(inv) for inv in run.invocations]

    if final:
        end = run.end or datetime.now()
        tj["run_summary"] = {
            "start":               run.start.isoformat(),
            "end":                 end.isoformat(),
            "elapsed_s":           (end - run.start).total_seconds(),
            "total_tokens_in":     sum(inv.tokens_in     for inv in run.invocations),
            "total_tokens_out":    sum(inv.tokens_out    for inv in run.invocations),
            "total_tokens_cached": sum(inv.tokens_cached for inv in run.invocations),
            "invocation_count":    len(run.invocations),
            "warnings":            list(run.warnings),
        }

    try:
        task_json_path.write_text(json.dumps(tj, indent=2) + "\n")
    except Exception:
        pass



def write_summary_to_readme(build_readme: Path | None, run: RunData) -> None:
    """Append the run summary as a ## Run Summary section to the Level:TOP README."""
    if build_readme is None or not build_readme.exists():
        return
    lines = ["", "## Run Summary", ""] + _build_summary_lines(run)
    with build_readme.open("a") as f:
        f.write("\n".join(lines))


def _build_summary_lines(run: RunData) -> list[str]:
    """Build the body lines shared by run-summary.md and the README section."""
    end = run.end or datetime.now()
    total = end - run.start
    lines = []

    total_in     = sum(inv.tokens_in     for inv in run.invocations)
    total_out    = sum(inv.tokens_out    for inv in run.invocations)
    total_cached = sum(inv.tokens_cached for inv in run.invocations)
    total_tokens = total_in + total_out + total_cached

    # Header table
    lines += [
        f"| Field          | Value |",
        f"|----------------|-------|",
        f"| Task           | {run.task_name} |",
        f"| Start          | {run.start.strftime('%Y-%m-%d %H:%M:%S')} |",
        f"| End            | {end.strftime('%Y-%m-%d %H:%M:%S')} |",
        f"| Total time     | {_fmt_elapsed(total)} |",
        f"| Invocations    | {len(run.invocations)} |",
        f"| Tokens in      | {total_in:,} |",
        f"| Tokens out     | {total_out:,} |",
        f"| Tokens cached  | {total_cached:,} |",
        f"| Tokens total   | {total_tokens:,} |",
        "",
    ]

    # Per-invocation table
    lines += [
        "### Invocations",
        "",
        "| # | Role | Agent | Description | Ended | Elapsed | Tokens In | Tokens Out | Tokens Cached |",
        "|---|------|-------|-------------|-------|---------|-----------|------------|---------------|",
    ]
    for i, inv in enumerate(run.invocations, 1):
        elapsed = _fmt_elapsed(inv.elapsed)
        lines.append(
            f"| {i} | {inv.role} | {inv.agent} | {inv.description} "
            f"| {inv.end.strftime('%H:%M:%S')} | {elapsed} "
            f"| {inv.tokens_in:,} | {inv.tokens_out:,} | {inv.tokens_cached:,} |"
        )
    lines.append("")

    # Per-role totals
    role_totals: dict[str, dict] = {}
    for inv in run.invocations:
        r = role_totals.setdefault(inv.role, {"count": 0, "total": timedelta()})
        r["count"] += 1
        r["total"] += inv.elapsed

    lines += ["### Per-Role Totals", "", "| Role | Count | Total Time | Avg/Invocation |",
              "|------|-------|------------|----------------|"]
    for role, data in role_totals.items():
        avg = data["total"] / data["count"]
        lines.append(f"| {role} | {data['count']} | {_fmt_elapsed(data['total'])} | {_fmt_elapsed(avg)} |")
    lines.append("")

    # Token usage by role
    role_tokens: dict[str, dict] = {}
    for inv in run.invocations:
        t = role_tokens.setdefault(inv.role, {"in": 0, "out": 0, "cached": 0})
        t["in"]     += inv.tokens_in
        t["out"]    += inv.tokens_out
        t["cached"] += inv.tokens_cached

    grand = {"in": 0, "out": 0, "cached": 0}
    lines += ["### Token Usage by Role", "",
              "| Role | Tokens In | Tokens Out | Tokens Cached | Total |",
              "|------|-----------|------------|---------------|-------|"]
    for role, t in role_tokens.items():
        total_tok = t["in"] + t["out"] + t["cached"]
        grand["in"]     += t["in"]
        grand["out"]    += t["out"]
        grand["cached"] += t["cached"]
        lines.append(f"| {role} | {t['in']:,} | {t['out']:,} | {t['cached']:,} | {total_tok:,} |")
    grand_total = grand["in"] + grand["out"] + grand["cached"]
    lines.append(f"| **Total** | **{grand['in']:,}** | **{grand['out']:,}** | **{grand['cached']:,}** | **{grand_total:,}** |")
    lines.append("")

    # Per-agent invocation counts
    agent_counts: dict[str, int] = {}
    for inv in run.invocations:
        agent_counts[inv.agent] = agent_counts.get(inv.agent, 0) + 1

    lines += ["### Invocations by Agent", "", "| Agent | Count |", "|-------|-------|"]
    for agent, count in sorted(agent_counts.items()):
        lines.append(f"| {agent} | {count} |")
    lines.append("")

    # Warnings — only included when there are retries to report
    if run.warnings:
        lines += ["## Warnings", ""]
        for w in run.warnings:
            lines.append(f"- {w}")
        lines.append("")

    return lines




# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _inv_dict(inv: InvocationRecord) -> dict:
    return {
        "role":          inv.role,
        "agent":         inv.agent,
        "n":             inv.n,
        "description":   inv.description,
        "start":         inv.start.isoformat(),
        "end":           inv.end.isoformat(),
        "elapsed_s":     inv.elapsed.total_seconds(),
        "tokens_in":     inv.tokens_in,
        "tokens_out":    inv.tokens_out,
        "tokens_cached": inv.tokens_cached,
        "outcome":       inv.outcome,
    }


def _fmt_elapsed(td: timedelta) -> str:
    total = int(td.total_seconds())
    m, s = divmod(total, 60)
    return f"{m}m {s:02d}s" if m else f"{s}s"
