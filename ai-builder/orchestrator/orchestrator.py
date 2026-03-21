import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from agent_wrapper import run_agent, AgentResult
import metrics as metrics_mod
from metrics import RunData, description_from_job_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

parser = argparse.ArgumentParser(description="AIDT+ orchestrator")
parser.add_argument(
    "--job",
    type=Path,
    help="Path to the job document (non-TM mode)",
)
parser.add_argument(
    "--output-dir",
    type=Path,
    required=True,
    help="Directory where generated artifacts and logs are written",
)
parser.add_argument(
    "--target-repo",
    type=Path,
    help="Path to the target repository (enables TM mode)",
)
parser.add_argument(
    "--epic",
    default="main",
    help="Epic name for the task system (TM mode only, default: main)",
)
parser.add_argument(
    "--state-machine",
    type=Path,
    metavar="FILE",
    help="Path to a JSON state machine file (optional; default inferred from mode)",
)
parser.add_argument(
    "--start-state",
    metavar="ROLE",
    help="Override the machine's start_state at runtime (e.g. for testing or resuming)",
)
parser.add_argument(
    "--resume",
    action="store_true",
    help="Resume a mid-run pipeline. Skips the Level: TOP entry-point validation so the "
         "orchestrator can restart from an INTERNAL task (e.g. after a rate-limit halt).",
)
parser.add_argument(
    "--clean-resume",
    action="store_true",
    help="Like --resume, but also deletes the interrupted component's output files before "
         "restarting. Items in OUTPUT_DIR newer than the last LEAF_COMPLETE_HANDLER entry "
         "are removed when the stall occurred during ARCHITECT or IMPLEMENTOR. TESTER stalls "
         "are left intact. Implies --resume.",
)
args = parser.parse_args()

if args.clean_resume:
    args.resume = True

TM_MODE = args.target_repo is not None

if TM_MODE:
    if not args.target_repo.exists():
        print(f"[orchestrator] Target repo not found: {args.target_repo}")
        sys.exit(1)

else:
    if not args.job:
        print("[orchestrator] --job is required when not using --target-repo")
        sys.exit(1)
    if not args.job.exists():
        print(f"[orchestrator] Job document not found: {args.job}")
        sys.exit(1)

REPO_ROOT       = Path(__file__).resolve().parent.parent.parent
ROLES_DIR       = REPO_ROOT / "roles"
MACHINES_DIR    = Path(__file__).resolve().parent / "machines"
OUTPUT_DIR      = args.output_dir.resolve()
TIMEOUT_MINUTES = 5

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
EXECUTION_LOG    = OUTPUT_DIR / "execution.log"
CURRENT_JOB_FILE = OUTPUT_DIR / "current-job.txt"

if TM_MODE:
    TARGET_REPO    = args.target_repo.resolve()
    EPIC           = args.epic
    PM_SCRIPTS_DIR = TARGET_REPO / "project" / "tasks" / "scripts"
    SETUP_SCRIPT   = REPO_ROOT / "target" / "setup-project.sh"
    INIT_SCRIPT    = REPO_ROOT / "target" / "init-claude-md.sh"
    # If Oracle pre-seeded current-job.txt (e.g. regression test setup), use it.
    if CURRENT_JOB_FILE.exists():
        initial_job_doc = Path(CURRENT_JOB_FILE.read_text().strip())
    else:
        initial_job_doc = None

    # Validate: TM mode requires a PIPELINE-SUBTASK with Level: TOP as entry point.
    if initial_job_doc is not None:
        if not initial_job_doc.exists():
            print(f"[orchestrator] Initial job document not found: {initial_job_doc}")
            sys.exit(1)
        _task_json = initial_job_doc.parent / "task.json"
        if not _task_json.exists():
            print(f"[orchestrator] ERROR: no task.json found alongside {initial_job_doc}.")
            print(f"    TM mode requires a pipeline subtask created with new-pipeline-build.sh.")
            sys.exit(1)
        _task_data = json.loads(_task_json.read_text())
        if _task_data.get("task-type") != "PIPELINE-SUBTASK":
            print(f"[orchestrator] ERROR: TM mode requires a PIPELINE-SUBTASK as the pipeline entry point.")
            print(f"    Job document: {initial_job_doc}")
            print(f"    task.json task-type is '{_task_data.get('task-type')}', expected 'PIPELINE-SUBTASK'.")
            print(f"    Create a pipeline build task with new-pipeline-build.sh.")
            sys.exit(1)
        if not args.resume and _task_data.get("level") != "TOP":
            print(f"[orchestrator] ERROR: TM mode requires the pipeline entry point to have level: TOP.")
            print(f"    Job document: {initial_job_doc}")
            print(f"    task.json level is '{_task_data.get('level')}', expected 'TOP'.")
            print(f"    (Use --resume to skip this check when restarting a mid-run pipeline.)")
            sys.exit(1)
else:
    initial_job_doc = args.job.resolve()


# ---------------------------------------------------------------------------
# State machine loader
# ---------------------------------------------------------------------------

def load_state_machine(machine_file: Path) -> tuple[dict, dict, str, dict, set[str]]:
    """Load and validate a machine JSON file.

    Returns (agents, routes, start_state, role_prompts, no_history_roles) where:
      agents           — maps role name → agent CLI name
      routes           — maps (role, outcome) → next role or None
      start_state      — default entry role
      role_prompts     — maps role → Path (prompt file) or None (dynamic generation)
      no_history_roles — set of roles that receive no handoff history in their prompt
    """
    try:
        data = json.loads(machine_file.read_text())
    except Exception as e:
        print(f"[orchestrator] Failed to load machine file {machine_file}: {e}")
        sys.exit(1)

    missing = [k for k in ("start_state", "roles", "transitions") if k not in data]
    if missing:
        print(f"[orchestrator] Machine file {machine_file} missing keys: {missing}")
        sys.exit(1)

    start_state = data["start_state"]
    roles       = data["roles"]
    transitions = data["transitions"]

    if start_state not in roles:
        print(f"[orchestrator] Machine file error: start_state '{start_state}' not in roles")
        sys.exit(1)

    agents = {role: cfg["agent"] for role, cfg in roles.items()}

    routes: dict[tuple[str, str], str | None] = {}
    for role, outcomes in transitions.items():
        if role not in roles:
            print(f"[orchestrator] Machine file error: transition source '{role}' not in roles")
            sys.exit(1)
        for outcome, next_role in outcomes.items():
            if next_role is not None and next_role not in roles:
                print(f"[orchestrator] Machine file error: transition {role}/{outcome} → "
                      f"'{next_role}' not in roles")
                sys.exit(1)
            routes[(role, outcome)] = next_role

    role_prompts: dict[str, Path | None] = {}
    for role, cfg in roles.items():
        if cfg["prompt"] is None:
            role_prompts[role] = None
        else:
            p = Path(cfg["prompt"])
            role_prompts[role] = p if p.is_absolute() else REPO_ROOT / p

    no_history_roles: set[str] = {
        role for role, cfg in roles.items() if cfg.get("no_history", False)
    }

    return agents, routes, start_state, role_prompts, no_history_roles


# ---------------------------------------------------------------------------
# Pipeline config — load state machine
# ---------------------------------------------------------------------------

if args.state_machine:
    _machine_file = args.state_machine.resolve()
    if not _machine_file.exists():
        print(f"[orchestrator] Machine file not found: {_machine_file}")
        sys.exit(1)
elif TM_MODE:
    _machine_file = MACHINES_DIR / "default.json"
else:
    _machine_file = MACHINES_DIR / "simple.json"

AGENTS, ROUTES, _start_state, ROLE_PROMPTS, NO_HISTORY_ROLES = load_state_machine(_machine_file)

if args.start_state:
    if args.start_state not in AGENTS:
        print(f"[orchestrator] --start-state '{args.start_state}' is not a valid role. "
              f"Valid roles: {', '.join(AGENTS)}")
        sys.exit(1)
    _start_state = args.start_state


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def build_prompt(role: str, job_doc: Path | None, output_dir: Path, handoff_history: list[str]) -> str:
    history_section = ""
    if handoff_history and role not in NO_HISTORY_ROLES:
        history_section = "\n\n## Handoff Notes from Previous Agents\n\n" + \
            "\n\n---\n\n".join(handoff_history)

    role_file = ROLE_PROMPTS.get(role) or (ROLES_DIR / f"{role}.md")
    role_instructions = role_file.read_text() if role_file.exists() \
        else "Complete the work described in the job document."
    if role == "ARCHITECT":
        # Read complexity and level from task.json (preferred) so the metadata
        # table is not needed in the prose README.
        task_json_path = job_doc.parent / "task.json" if job_doc else None
        if task_json_path and task_json_path.exists():
            try:
                task_data = json.loads(task_json_path.read_text())
                complexity = task_data.get("complexity", "—")
                level = task_data.get("level", "TOP")
            except Exception:
                complexity, level = "—", "TOP"
        else:
            complexity, level = "—", "TOP"
        if complexity == "atomic":
            valid_outcomes = "ARCHITECT_DESIGN_READY | ARCHITECT_NEEDS_REVISION | ARCHITECT_NEED_HELP"
        elif complexity in ("composite", "—"):
            valid_outcomes = "ARCHITECT_DECOMPOSITION_READY | ARCHITECT_NEEDS_REVISION | ARCHITECT_NEED_HELP"
        else:
            valid_outcomes = "ARCHITECT_DESIGN_READY | ARCHITECT_DECOMPOSITION_READY | ARCHITECT_NEED_HELP"
        job_section = (
            f"\nThe shared job document is at: {job_doc}\n"
            f"Task Level: {level}\n"
            f"\nOutput directory (write all generated files here): {output_dir}\n"
        )
    elif role == "IMPLEMENTOR":
        valid_outcomes = "IMPLEMENTOR_IMPLEMENTATION_DONE | IMPLEMENTOR_NEEDS_ARCHITECT | IMPLEMENTOR_NEED_HELP"
        job_section = f"\nThe shared job document is at: {job_doc}\n\nOutput directory (write all generated files here): {output_dir}\n"
    elif role == "TESTER":
        valid_outcomes = "TESTER_TESTS_PASS | TESTER_TESTS_FAIL | TESTER_NEED_HELP"
        job_section = f"\nThe shared job document is at: {job_doc}\n\nOutput directory (write all generated files here): {output_dir}\n"
    else:
        valid_outcomes = "DONE | NEED_HELP"
        job_section = f"\nThe shared job document is at: {job_doc}\n\nOutput directory (write all generated files here): {output_dir}\n"

    return f"""Your role is {role}.
{job_section}
{role_instructions}
{history_section}

When you are finished, end your response with exactly this block (fill in the values):

OUTCOME: {valid_outcomes}
HANDOFF: one paragraph summarising what you did and what the next agent needs to know
"""


# ---------------------------------------------------------------------------
# Outcome parser
# ---------------------------------------------------------------------------

def parse_outcome(response: str) -> tuple[str, str]:
    outcome_match = re.search(r'^OUTCOME:\s*(\S+)', response, re.MULTILINE)
    handoff_match = re.search(r'^HANDOFF:\s*(.+)', response, re.MULTILINE | re.DOTALL)

    outcome = outcome_match.group(1).strip() if outcome_match else "UNKNOWN"
    handoff = handoff_match.group(1).strip() if handoff_match else "(no handoff provided)"
    return outcome, handoff


# ---------------------------------------------------------------------------
# Internal agents — deterministic roles that run shell scripts directly
# in Python rather than spawning a claude subprocess.
#
# An "internal" agent is declared in the machine JSON with "agent": "internal".
# It returns an AgentResult with zero token counts (no model was invoked).
# ---------------------------------------------------------------------------

def _parse_components_table(readme_text: str) -> list[dict]:
    """Parse the Markdown Components table from a README.

    Expects a table under ## Components with columns: Name | Complexity | Description.
    Returns a list of dicts with keys 'name', 'complexity', 'description'.
    Preserves row order; skips the header and separator rows.
    """
    components_match = re.search(r'## Components\s*\n(.*?)(?=\n## |\Z)', readme_text, re.DOTALL)
    if not components_match:
        return []

    section = components_match.group(1)
    rows = []
    in_table = False
    header_seen = False
    sep_seen = False
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith('|'):
            if in_table:
                break
            continue
        if not in_table and 'Name' in stripped:
            in_table = True
            header_seen = True
            continue
        if header_seen and not sep_seen:
            sep_seen = True  # skip separator row (|---|---|---|)
            continue
        parts = [p.strip() for p in stripped.split('|')]
        parts = [p for p in parts if p]  # drop empty strings from leading/trailing |
        if len(parts) >= 3:
            rows.append({
                "name": parts[0],
                "complexity": parts[1],
                "description": "|".join(parts[2:]).strip(),  # description may contain |
            })
    return rows


def _run_decompose_internal(job_doc: Path, output_dir: Path) -> AgentResult:
    """Execute DECOMPOSE_HANDLER logic directly without a claude subprocess.

    Reads the Markdown Components table from the parent job doc, creates a
    pipeline subtask for each component via new-pipeline-subtask.sh, fills
    in Goal/Context in each subtask README, sets metadata in each task.json,
    and points current-job.txt at the first subtask.
    """
    parent_dir = job_doc.parent
    task_json_path = parent_dir / "task.json"
    if not task_json_path.exists():
        return AgentResult(exit_code=1, response=f"task.json not found at {task_json_path}")

    try:
        parent_data = json.loads(task_json_path.read_text())
    except Exception as e:
        return AgentResult(exit_code=1, response=f"Failed to parse task.json: {e}")

    parent_level = parent_data.get("level", "TOP")

    components = _parse_components_table(job_doc.read_text())
    if not components:
        return AgentResult(exit_code=1, response="No components found in ## Components table")

    # Determine parent's path relative to in-progress/ (for --parent flag)
    in_progress_dir = TARGET_REPO / "project" / "tasks" / EPIC / "in-progress"
    try:
        parent_rel = str(parent_dir.relative_to(in_progress_dir))
    except ValueError:
        return AgentResult(exit_code=1, response=f"Cannot compute parent rel path: {parent_dir}")

    # Extract parent Goal + Context to inject into subtask Context sections
    parent_content = job_doc.read_text()
    goal_match = re.search(r'## Goal\s*\n\n(.*?)(?=\n## |\Z)', parent_content, re.DOTALL)
    parent_goal = goal_match.group(1).strip() if goal_match else ""
    context_match = re.search(r'## Context\s*\n\n(.*?)(?=\n## |\Z)', parent_content, re.DOTALL)
    parent_context = context_match.group(1).strip() if context_match else ""

    subtask_dirs = []
    for i, component in enumerate(components):
        comp_name = component["name"]
        complexity = component["complexity"]
        description = component["description"]

        cmd = [
            str(PM_SCRIPTS_DIR / "new-pipeline-subtask.sh"),
            "--epic", EPIC,
            "--folder", "in-progress",
            "--parent", parent_rel,
            "--name", comp_name,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            err = proc.stderr.strip() or proc.stdout.strip()
            return AgentResult(exit_code=1, response=f"new-pipeline-subtask.sh failed for '{comp_name}': {err}")

        # Parse created subtask relative path from script output
        created_rel = None
        for line in proc.stdout.splitlines():
            if line.startswith("Created pipeline-subtask:"):
                created_rel = line.split(": ", 1)[1].strip().rstrip("/")
                break
        if created_rel is None:
            return AgentResult(exit_code=1, response=f"Cannot parse subtask path from: {proc.stdout!r}")

        subtask_dir = TARGET_REPO / created_rel
        subtask_dirs.append(subtask_dir)

        # Update task.json: set complexity; for last component also set last-task + level
        subtask_json = subtask_dir / "task.json"
        if subtask_json.exists():
            try:
                subtask_data = json.loads(subtask_json.read_text())
                subtask_data["complexity"] = complexity
                if i == len(components) - 1:
                    subtask_data["last-task"] = True
                    subtask_data["level"] = parent_level
                subtask_json.write_text(json.dumps(subtask_data, indent=2) + "\n")
            except Exception as e:
                return AgentResult(exit_code=1, response=f"Failed to update subtask task.json for '{comp_name}': {e}")

        # Update README: Goal = component description, Context = parent goal + context
        subtask_readme = subtask_dir / "README.md"
        if subtask_readme.exists():
            readme = subtask_readme.read_text()
            readme = readme.replace(
                "## Goal\n\n_To be written._",
                f"## Goal\n\n{description}",
            )
            context_body = parent_goal
            if parent_context and parent_context != "_To be written._":
                context_body += f"\n\n{parent_context}"
            readme = readme.replace(
                "## Context\n\n_To be written._",
                f"## Context\n\n{context_body}",
            )
            subtask_readme.write_text(readme)

    if not subtask_dirs:
        return AgentResult(exit_code=1, response="No subtasks created")

    # Point pipeline at first subtask
    first_readme = subtask_dirs[0] / "README.md"
    cmd = [
        str(PM_SCRIPTS_DIR / "set-current-job.sh"),
        "--output-dir", str(output_dir),
        str(first_readme),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        err = proc.stderr.strip() or proc.stdout.strip()
        return AgentResult(exit_code=1, response=f"set-current-job.sh failed: {err}")

    response = (
        f"OUTCOME: HANDLER_SUBTASKS_READY\n"
        f"HANDOFF: decomposed into {len(components)} components "
        f"(level={parent_level}), first: {subtask_dirs[0].name}"
    )
    return AgentResult(exit_code=0, response=response)


def _run_lch_internal(output_dir: Path) -> AgentResult:
    """Execute LEAF_COMPLETE_HANDLER logic directly without a claude subprocess.

    Runs on-task-complete.sh and maps its three possible outputs to the
    corresponding outcome strings. No AI reasoning is required for this role.
    """
    current_job_path = CURRENT_JOB_FILE.read_text().strip()
    cmd = [
        str(PM_SCRIPTS_DIR / "on-task-complete.sh"),
        "--current", current_job_path,
        "--output-dir", str(output_dir),
        "--epic", EPIC,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    stdout = proc.stdout.strip()

    if proc.returncode != 0:
        err = proc.stderr.strip() or stdout
        print(f"[internal/LCH] on-task-complete.sh failed (exit {proc.returncode}): {err}")
        return AgentResult(exit_code=1, response=f"on-task-complete.sh failed: {err}")

    # on-task-complete.sh may emit status lines before the terminal token.
    # Scan each line for NEXT/DONE/STOP_AFTER rather than matching the whole blob.
    outcome = None
    token_line = ""
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line.startswith("NEXT "):
            outcome = "HANDLER_SUBTASKS_READY"
            token_line = line
            break
        elif line == "DONE":
            outcome = "HANDLER_ALL_DONE"
            token_line = line
            break
        elif line == "STOP_AFTER":
            outcome = "HANDLER_STOP_AFTER"
            token_line = line
            break

    if outcome is None:
        print(f"[internal/LCH] unexpected output from on-task-complete.sh: {stdout!r}")
        return AgentResult(exit_code=1, response=f"Unexpected output: {stdout}")

    response = f"OUTCOME: {outcome}\nHANDOFF: ran on-task-complete.sh → {token_line}"
    return AgentResult(exit_code=0, response=response)


def run_internal_agent(role: str, output_dir: Path, job_doc: Path | None) -> AgentResult:
    """Dispatch to the internal implementation for the given role."""
    if role == "LEAF_COMPLETE_HANDLER":
        return _run_lch_internal(output_dir)
    if role == "DECOMPOSE_HANDLER":
        if job_doc is None:
            return AgentResult(exit_code=1, response="DECOMPOSE_HANDLER requires a job_doc")
        return _run_decompose_internal(job_doc, output_dir)
    return AgentResult(exit_code=1, response=f"No internal implementation for role: {role}")


# ---------------------------------------------------------------------------
# Execution log helpers
# ---------------------------------------------------------------------------

def log_run(role: str, agent: str, outcome: str, handoff: str) -> None:
    with EXECUTION_LOG.open("a") as f:
        f.write(f"\n{'=' * 60}\n")
        f.write(f"[{datetime.now().isoformat()}] {role}/{agent}\n")
        f.write(f"OUTCOME: {outcome}\n")
        f.write(f"HANDOFF: {handoff}\n")


# ---------------------------------------------------------------------------
# Clean-resume helpers
# ---------------------------------------------------------------------------

_CLEAN_RESUME_PROTECTED = frozenset({
    "runs", "current-job.txt", "execution.log",
    "run-metrics.json", "run-summary.md",
})

_LOG_RUN_LINE = re.compile(r'^\[([^\]]+)\] ([A-Z_]+)/')


def _last_lch_timestamp(execution_log: Path) -> datetime | None:
    """Return the datetime of the last LEAF_COMPLETE_HANDLER log_run entry, or None."""
    if not execution_log.exists():
        return None
    lch_pattern = re.compile(r'^\[([^\]]+)\] LEAF_COMPLETE_HANDLER/')
    last_ts = None
    for line in execution_log.read_text().splitlines():
        m = lch_pattern.match(line)
        if m:
            try:
                last_ts = datetime.fromisoformat(m.group(1))
            except ValueError:
                pass
    return last_ts


def _last_stalled_role(execution_log: Path) -> str | None:
    """Return the role name from the last log_run entry in execution.log, or None."""
    if not execution_log.exists():
        return None
    last_role = None
    for line in execution_log.read_text().splitlines():
        m = _LOG_RUN_LINE.match(line)
        if m:
            last_role = m.group(2)
    return last_role


def _clean_for_resume(output_dir: Path, execution_log: Path) -> None:
    """Delete the interrupted component's output files before resuming.

    Stall-during rules:
      - ARCHITECT or IMPLEMENTOR stall: delete OUTPUT_DIR items newer than the
        last LEAF_COMPLETE_HANDLER timestamp (delete everything unprotected if
        no LCH has ever run).
      - TESTER stall or unknown: leave output intact.

    Protected names are never deleted: runs/, current-job.txt, execution.log,
    run-metrics.json, run-summary.md.
    """
    stalled_role = _last_stalled_role(execution_log)
    if stalled_role not in ("ARCHITECT", "IMPLEMENTOR"):
        if stalled_role is None:
            print("[orchestrator] --clean-resume: no prior run found in execution.log; nothing to clean.")
        else:
            print(f"[orchestrator] --clean-resume: stalled role was {stalled_role}; "
                  f"leaving output intact (TESTER stall).")
        return

    lch_ts = _last_lch_timestamp(execution_log)
    if lch_ts is None:
        print(f"[orchestrator] --clean-resume: stalled during {stalled_role}, "
              f"no prior LEAF_COMPLETE_HANDLER; deleting all unprotected output items.")
        cutoff_ts = None
    else:
        cutoff_ts = lch_ts
        print(f"[orchestrator] --clean-resume: stalled during {stalled_role}; "
              f"deleting output items newer than last LCH ({lch_ts.isoformat()}).")

    deleted = []
    for item in output_dir.iterdir():
        if item.name in _CLEAN_RESUME_PROTECTED:
            continue
        item_mtime = datetime.fromtimestamp(item.stat().st_mtime)
        if cutoff_ts is None or item_mtime > cutoff_ts:
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
            deleted.append(item.name)

    if deleted:
        print(f"    deleted {len(deleted)} item(s): {', '.join(sorted(deleted))}")
    else:
        print("    nothing to delete.")


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

MAX_ROLE_ITERATIONS = 3

current_role = _start_state
job_doc      = initial_job_doc
handoff_history: list[str] = []
# Stack of decomposition frames for scope-bounded handoff history.
# Each frame: {"anchor_index": int, "scope_dir": Path}
# anchor_index — index in handoff_history of the DECOMPOSE_HANDLER entry that opened this frame.
# scope_dir    — job_doc.parent at the moment DECOMPOSE_HANDLER fired; equals the parent
#                directory of every subtask created by that decomposition.
frame_stack: list[dict] = []
role_iteration_counts: dict[str, int] = {}
role_counters: dict[str, int] = {}

# Metrics state
_task_name = description_from_job_path(initial_job_doc) if initial_job_doc else "pipeline"
run = RunData(task_name=_task_name, start=datetime.now())
build_readme: Path | None = None  # Level:TOP pipeline-subtask README for live log


def _find_level_top(readme: Path | None) -> Path | None:
    """Return the nearest README (at or above readme's directory) whose task.json has level: TOP.

    Walks upward through parent directories so that resuming from an INTERNAL
    task still finds the Level: TOP build-N README that owns the execution log.
    """
    if not readme:
        return None
    candidate = readme
    while candidate and candidate.exists():
        task_json = candidate.parent / "task.json"
        if task_json.exists():
            try:
                data = json.loads(task_json.read_text())
                if data.get("level") == "TOP":
                    return candidate
            except Exception:
                pass
        parent_readme = candidate.parent.parent / "README.md"
        if parent_readme == candidate:
            break
        candidate = parent_readme
    return None

build_readme = _find_level_top(initial_job_doc)

if args.clean_resume:
    _clean_for_resume(OUTPUT_DIR, EXECUTION_LOG)

print("=== Orchestrator: starting ===")
if TM_MODE:
    print(f"    mode:          TM")
    print(f"    target repo:   {TARGET_REPO}")
    print(f"    epic:          {EPIC}")
else:
    print(f"    job doc:       {job_doc}")
print(f"    machine file:  {_machine_file}")
print(f"    start state:   {current_role}")
print(f"    output dir:    {OUTPUT_DIR}")
print(f"    execution log: {EXECUTION_LOG}\n")

while current_role is not None:
    agent = AGENTS.get(current_role)
    if agent is None:
        print(f"[orchestrator] No agent configured for role {current_role}. Halting.")
        sys.exit(1)

    print(f"\n>>> [{current_role} / {agent}]")

    inv_start = datetime.now()
    if agent == "internal":
        result: AgentResult = run_internal_agent(current_role, OUTPUT_DIR, job_doc)
    else:
        prompt = build_prompt(current_role, job_doc, OUTPUT_DIR, handoff_history)
        result = run_agent(agent, TIMEOUT_MINUTES, current_role, prompt, OUTPUT_DIR)
    inv_end = datetime.now()

    if result.exit_code == 2:
        print(f"\n[orchestrator] {current_role} timed out. Halting.")
        sys.exit(1)
    if result.exit_code == 1:
        print(f"\n[orchestrator] {current_role} agent error. Halting.")
        sys.exit(1)

    outcome, handoff = parse_outcome(result.response)
    handoff_history.append(f"[{current_role}] {handoff}")
    log_run(current_role, agent, outcome, handoff)

    print(f"\n<<< [{current_role}] outcome={outcome}")

    # Record metrics
    role_counters[current_role] = role_counters.get(current_role, 0) + 1
    metrics_mod.record_invocation(
        run=run,
        role=current_role,
        agent=agent,
        role_counter=role_counters[current_role],
        description=description_from_job_path(job_doc),
        start=inv_start,
        end=inv_end,
        tokens_in=result.tokens_in,
        tokens_out=result.tokens_out,
        tokens_cached=result.tokens_cached,
        outcome=outcome,
    )

    # Update live execution log in the Level:TOP README
    if build_readme is None:
        build_readme = _find_level_top(job_doc)
    if build_readme is not None:
        metrics_mod.update_task_doc(build_readme, run)

    if outcome.endswith("_NEED_HELP"):
        print(f"\n[orchestrator] {current_role} needs human help. Halting.")
        if job_doc:
            print(f"    Review the job document: {job_doc}")
        sys.exit(0)

    if outcome not in [o for (_, o) in ROUTES]:
        print(f"\n[orchestrator] Unrecognised outcome '{outcome}' from {current_role}. Halting.")
        sys.exit(1)

    # After a handler signals HANDLER_SUBTASKS_READY, read the current job path for downstream agents.
    # DECOMPOSE: push a new frame BEFORE job_doc is updated (scope_dir = current job_doc.parent).
    # LEAF:      pop frames and truncate handoff history AFTER job_doc is updated (uses next job path).
    if current_role in ("DECOMPOSE_HANDLER", "LEAF_COMPLETE_HANDLER") and outcome == "HANDLER_SUBTASKS_READY":
        if not CURRENT_JOB_FILE.exists():
            print(f"\n[orchestrator] Handler did not write job path to {CURRENT_JOB_FILE}. Halting.")
            sys.exit(1)

        if current_role == "DECOMPOSE_HANDLER" and job_doc:
            frame_stack.append({
                "anchor_index": len(handoff_history) - 1,
                "scope_dir": job_doc.parent,
            })

        job_doc = Path(CURRENT_JOB_FILE.read_text().strip())
        if not job_doc.exists():
            print(f"\n[orchestrator] Job document not found: {job_doc}. Halting.")
            sys.exit(1)
        print(f"    current job:   {job_doc}")
        if build_readme is None:
            build_readme = _find_level_top(job_doc)

        if current_role == "LEAF_COMPLETE_HANDLER":
            # Pop frames whose scope doesn't contain the next task, then truncate.
            while frame_stack and frame_stack[-1]["scope_dir"] != job_doc.parent:
                frame_stack.pop()
            if frame_stack:
                handoff_history[:] = handoff_history[:frame_stack[-1]["anchor_index"] + 1]
            else:
                handoff_history.clear()

    next_role = ROUTES.get((current_role, outcome))

    if next_role == current_role:
        role_iteration_counts[current_role] = role_iteration_counts.get(current_role, 0) + 1
        if role_iteration_counts[current_role] >= MAX_ROLE_ITERATIONS:
            print(f"\n[orchestrator] {current_role} has self-routed {role_iteration_counts[current_role]} times "
                  f"(outcome='{outcome}'). Iteration limit ({MAX_ROLE_ITERATIONS}) reached. Halting.")
            print(f"    Review the job document and role prompt for {current_role}.")
            if job_doc:
                print(f"    Job document: {job_doc}")
            sys.exit(1)
    else:
        role_iteration_counts.pop(current_role, None)

    current_role = next_role

run.end = datetime.now()
metrics_mod.write_run_summary(OUTPUT_DIR, run)
metrics_mod.write_run_metrics_json(OUTPUT_DIR, run)
metrics_mod.write_summary_to_readme(build_readme, run)

print("\n=== Orchestrator: pipeline complete ===")
