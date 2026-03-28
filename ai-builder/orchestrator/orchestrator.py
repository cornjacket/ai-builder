import argparse
import atexit
import html
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

from agent_wrapper import run_agent, AgentResult
from gemini_compat import gemini_role_addendum
import metrics as metrics_mod
from metrics import RunData, InvocationRecord, description_from_job_path
from render_readme import render_task_readme
from build_master_index import build_master_index


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

parser = argparse.ArgumentParser(description="AIDT+ orchestrator")
parser.add_argument(
    "--job",
    type=Path,
    help="Path to the TOP-level pipeline README.md (required in TM mode unless --resume)",
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
    "--run-dir",
    type=Path,
    metavar="DIR",
    help="Directory for per-run coordination files (execution.log, current-job.txt, "
         "handoff-state.json, last-job.json). Defaults to --output-dir. Set to a "
         "unique path per invocation to run multiple pipelines concurrently.",
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
parser.add_argument(
    "--handoff-file",
    type=Path,
    metavar="FILE",
    help="JSON file to pre-populate handoff_history and frame_stack at startup. "
         "When --resume is passed, handoff-state.json in the output directory is "
         "loaded automatically (this flag is not needed for normal resumes).",
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

# RUN_DIR holds per-run coordination files (execution.log, current-job.txt,
# handoff-state.json, last-job.json). Defaults to OUTPUT_DIR for backward
# compatibility. Set --run-dir to a unique path per invocation to support
# concurrent pipeline runs without coordination file collisions.
RUN_DIR = args.run_dir.resolve() if args.run_dir else OUTPUT_DIR

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
RUN_DIR.mkdir(parents=True, exist_ok=True)
EXECUTION_LOG       = RUN_DIR / "execution.log"
CURRENT_JOB_FILE    = RUN_DIR / "current-job.txt"
LAST_JOB_FILE       = RUN_DIR / "last-job.json"
HANDOFF_STATE_FILE  = RUN_DIR / "handoff-state.json"

if TM_MODE:
    TARGET_REPO    = args.target_repo.resolve()
    EPIC           = args.epic
    PM_SCRIPTS_DIR = TARGET_REPO / "project" / "tasks" / "scripts"
    SETUP_SCRIPT   = REPO_ROOT / "target" / "setup-project.sh"
    INIT_SCRIPT    = REPO_ROOT / "target" / "init-claude-md.sh"

    # Resolve initial job doc: --job takes precedence; --resume falls back to
    # last-job.json written by a previous run.
    if args.job:
        initial_job_doc = args.job.resolve()
    elif args.resume and LAST_JOB_FILE.exists():
        try:
            _last = json.loads(LAST_JOB_FILE.read_text())
            initial_job_doc = Path(_last["active_task"]).parent / "README.md"
        except Exception as e:
            print(f"[orchestrator] ERROR: failed to read {LAST_JOB_FILE}: {e}")
            sys.exit(1)
    else:
        print("[orchestrator] --job is required in TM mode (or use --resume with a prior last-job.json)")
        sys.exit(1)

    # Validate: TM mode requires a PIPELINE-SUBTASK with Level: TOP as entry point.
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

def build_prompt(role: str, job_doc: Path | None, output_dir: Path, handoff_history: list[str], agent: str = "") -> str:
    history_section = ""
    if handoff_history and role not in NO_HISTORY_ROLES:
        history_section = "\n\n## Handoff Notes from Previous Agents\n\n" + \
            "\n\n---\n\n".join(handoff_history)

    role_file = ROLE_PROMPTS.get(role) or (ROLES_DIR / f"{role}.md")
    role_instructions = role_file.read_text() if role_file.exists() \
        else "Complete the work described in the job document."
    if role == "ARCHITECT":
        # Read complexity, level, goal, context from in-memory task_state.
        # task.json was loaded into task_state when job_doc was last set —
        # no disk read needed here. Falls back gracefully for edge cases.
        # See: learning/pipeline-extract-dont-delegate.md (Gemini cwd isolation)
        complexity   = task_state.get("complexity", "—")
        level        = task_state.get("level", "TOP")
        goal_text    = task_state.get("goal", "")
        context_text = task_state.get("context", "")
        if complexity == "atomic":
            valid_outcomes = "ARCHITECT_DESIGN_READY | ARCHITECT_NEEDS_REVISION | ARCHITECT_NEED_HELP"
        elif complexity in ("composite", "—"):
            valid_outcomes = "ARCHITECT_DECOMPOSITION_READY | ARCHITECT_NEEDS_REVISION | ARCHITECT_NEED_HELP"
        else:
            valid_outcomes = "ARCHITECT_DESIGN_READY | ARCHITECT_DECOMPOSITION_READY | ARCHITECT_NEED_HELP"
        if not goal_text:
            task_json_path = job_doc.parent / "task.json" if job_doc else None
            print(f"[orchestrator] ERROR: 'goal' missing from task state for {task_json_path}. "
                  f"Port this build to include goal/context in task.json (see 49352f-0000).")
            return
        goal_section = f"\n\n## Goal\n\n{goal_text}" if goal_text else ""
        context_section = f"\n\n## Context\n\n{context_text}" if context_text else ""
        job_section = (
            f"\nThe shared job document is at: {job_doc}\n"
            f"Task Level: {level}\n"
            f"Complexity: {complexity}\n"
            f"\nOutput directory (write all generated files here): {output_dir}\n"
            f"{goal_section}{context_section}\n"
        )
    elif role == "IMPLEMENTOR":
        valid_outcomes = "IMPLEMENTOR_IMPLEMENTATION_DONE | IMPLEMENTOR_NEEDS_ARCHITECT | IMPLEMENTOR_NEED_HELP"
        if not job_doc:
            print("[orchestrator] ERROR: IMPLEMENTOR requires a job_doc but none is set.")
            return
        # Read design fields from in-memory task_state — set when ARCHITECT
        # returned ARCHITECT_DESIGN_READY. No disk read needed.
        if not task_state.get("goal"):
            task_json_path = job_doc.parent / "task.json"
            print(f"[orchestrator] ERROR: 'goal' missing from task state for {task_json_path}.")
            return
        if not task_state.get("design"):
            task_json_path = job_doc.parent / "task.json"
            print(f"[orchestrator] ERROR: 'design' missing from task state for {task_json_path}. "
                  f"ARCHITECT must have returned ARCHITECT_DESIGN_READY before IMPLEMENTOR runs.")
            return
        inline_sections = ""
        for label, key in (
            ("Goal", "goal"),
            ("Context", "context"),
            ("Design", "design"),
            ("Acceptance Criteria", "acceptance_criteria"),
            ("Test Command", "test_command"),
        ):
            text = task_state.get(key, "").strip()
            if text and text != "_To be written._":
                inline_sections += f"\n\n## {label}\n\n{text}"
        job_section = (
            f"\nOutput directory (write all generated files here): {output_dir}\n"
            f"{inline_sections}\n"
        )
    else:
        valid_outcomes = "DONE | NEED_HELP"
        job_section = f"\nThe shared job document is at: {job_doc}\n\nOutput directory (write all generated files here): {output_dir}\n"

    agent_addendum = gemini_role_addendum(role) if agent == "gemini" else ""

    # ARCHITECT uses a terminal XML <response> block (defined in roles/ARCHITECT.md)
    # that already includes outcome, handoff, and design fields. Appending the
    # generic OUTCOME/HANDOFF footer would conflict with that instruction.
    if role == "ARCHITECT":
        return f"""Your role is {role}.
{job_section}
{role_instructions}
{history_section}{agent_addendum}"""

    return f"""Your role is {role}.
{job_section}
{role_instructions}
{history_section}{agent_addendum}
When you are finished, end your response with exactly this block (fill in the values):

OUTCOME: {valid_outcomes}
HANDOFF: one paragraph summarising what you did and what the next agent needs to know
"""


# ---------------------------------------------------------------------------
# XML helpers (for ARCHITECT responses)
# ---------------------------------------------------------------------------

def _extract_xml_tag(text: str, tag: str) -> str:
    m = re.search(rf'<{tag}>(.*?)</{tag}>', text, re.DOTALL)
    return html.unescape(m.group(1).strip()) if m else ""

def _extract_xml_components(text: str) -> list[dict]:
    components = []
    for block in re.findall(r'<component>(.*?)</component>', text, re.DOTALL):
        comp = {field: _extract_xml_tag(block, field)
                for field in ("name", "complexity", "source_dir", "description")}
        if comp.get("name"):
            components.append(comp)
    return components


# ---------------------------------------------------------------------------
# Outcome parser
# ---------------------------------------------------------------------------

def parse_response(response: str) -> tuple[str, str, list[dict]]:
    """Extract outcome, handoff, and components from an agent response.

    Tries XML <response> block first (ARCHITECT), falls back to terminal
    ```json block, then falls back to OUTCOME:/HANDOFF: lines (internal agents).
    """
    xml_match = re.search(r'<response>(.*?)</response>', response, re.DOTALL)
    if xml_match:
        block = xml_match.group(0)
        outcome = _extract_xml_tag(block, "outcome") or "UNKNOWN"
        handoff = _extract_xml_tag(block, "handoff") or "(no handoff provided)"
        components = _extract_xml_components(block)
        return outcome, handoff, components

    json_match = re.search(r'```json\s*\n(\{.*?\})\s*```\s*$', response, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group(1))
            outcome = data.get("outcome", "UNKNOWN")
            handoff = data.get("handoff", "(no handoff provided)")
            components = data.get("components", [])
            return outcome, handoff, components
        except json.JSONDecodeError as e:
            print(f"[orchestrator] ERROR: terminal JSON block found but failed to parse: {e}")
            print(f"[orchestrator] Raw JSON block:\n{json_match.group(1)}")
            raise SystemExit(1)

    # Fallback: plain OUTCOME:/HANDOFF: lines (internal agents)
    outcome_match = re.search(r'^OUTCOME:\s*(\S+)', response, re.MULTILINE)
    handoff_match = re.search(r'^HANDOFF:\s*(.+)', response, re.MULTILINE | re.DOTALL)
    outcome = outcome_match.group(1).strip() if outcome_match else "UNKNOWN"
    handoff = handoff_match.group(1).strip() if handoff_match else "(no handoff provided)"
    return outcome, handoff, []


# ---------------------------------------------------------------------------
# Internal agents — deterministic roles that run shell scripts directly
# in Python rather than spawning a claude subprocess.
#
# An "internal" agent is declared in the machine JSON with "agent": "internal".
# It returns an AgentResult with zero token counts (no model was invoked).
# ---------------------------------------------------------------------------

def _run_decompose_internal(job_doc: Path, components: list[dict]) -> AgentResult:
    """Execute DECOMPOSE_HANDLER logic directly without a claude subprocess.

    Receives the components array from ARCHITECT's JSON response (already parsed
    by the orchestrator). Creates a pipeline subtask and output subdirectory for
    each component, stores output_dir in each task.json, fills in Goal/Context,
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
    parent_depth = parent_data.get("depth", 0)
    child_depth  = parent_depth + 1
    parent_output_dir = Path(parent_data.get("output_dir", str(OUTPUT_DIR)))

    if not components:
        return AgentResult(exit_code=1, response="No components provided to DECOMPOSE_HANDLER")

    # Determine parent's path relative to in-progress/ (for --parent flag)
    in_progress_dir = TARGET_REPO / "project" / "tasks" / EPIC / "in-progress"
    try:
        parent_rel = str(parent_dir.relative_to(in_progress_dir))
    except ValueError:
        return AgentResult(exit_code=1, response=f"Cannot compute parent rel path: {parent_dir}")

    # Extract parent name and goal to append as a new ancestry level in child context.
    # The child's ## Context is built as a labelled chain: one ### Level N entry per
    # ancestor, newest appended last. This prevents the flat-copy duplication that
    # occurs when context is copied verbatim at each descent.
    parent_content = job_doc.read_text()
    goal_match = re.search(r'## Goal\s*\n\n(.*?)(?=\n## |\Z)', parent_content, re.DOTALL)
    parent_goal = goal_match.group(1).strip() if goal_match else ""
    context_match = re.search(r'## Context\s*\n\n(.*?)(?=\n## |\Z)', parent_content, re.DOTALL)
    parent_context = context_match.group(1).strip() if context_match else ""
    # Suppress placeholder context from freshly created tasks
    if parent_context == "_To be written._":
        parent_context = ""

    # Build the new ancestry entry for this level
    parent_task_name = parent_dir.name
    new_level_entry = f"### Level {child_depth} — {parent_task_name}\n{parent_goal}"

    # Compose child context: inherited chain + new entry for this level
    if parent_context:
        child_context = f"{parent_context}\n\n{new_level_entry}"
    else:
        child_context = new_level_entry

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

        # Determine output directory for this component
        source_dir = component.get("source_dir", "").strip()
        if comp_name == "integrate" or not source_dir or source_dir == ".":
            comp_output_dir = parent_output_dir  # integrate writes to parent dir directly
        else:
            comp_output_dir = parent_output_dir / source_dir
            comp_output_dir.mkdir(parents=True, exist_ok=True)
            placeholder = comp_output_dir / "README.md"
            if not placeholder.exists():
                placeholder.write_text(f"# {comp_name}\n\n_Placeholder. ARCHITECT fills in documentation._\n")

        # Update task.json: set complexity, depth, goal, context, output_dir;
        # for last component also set last-task + level
        subtask_json = subtask_dir / "task.json"
        if subtask_json.exists():
            try:
                subtask_data = json.loads(subtask_json.read_text())
                subtask_data["name"] = comp_name
                subtask_data["complexity"] = complexity
                subtask_data["depth"] = child_depth
                subtask_data["goal"] = description
                subtask_data["context"] = child_context
                subtask_data["output_dir"] = str(comp_output_dir)
                if i == len(components) - 1:
                    subtask_data["last-task"] = True
                    subtask_data["level"] = parent_level
                subtask_json.write_text(json.dumps(subtask_data, indent=2) + "\n")
            except Exception as e:
                return AgentResult(exit_code=1, response=f"Failed to update subtask task.json for '{comp_name}': {e}")

        # Update README: Goal = component description, Context = ancestry chain
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

    # Point pipeline at first subtask.
    # Write current-job.txt to RUN_DIR (== OUTPUT_DIR by default) — that is
    # where the orchestrator reads CURRENT_JOB_FILE from.
    first_readme = subtask_dirs[0] / "README.md"
    cmd = [
        str(PM_SCRIPTS_DIR / "set-current-job.sh"),
        "--output-dir", str(RUN_DIR),
        str(first_readme),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        err = proc.stderr.strip() or proc.stdout.strip()
        return AgentResult(exit_code=1, response=f"set-current-job.sh failed: {err}")

    # Check stop-after on the parent task.  When set, the orchestrator pauses
    # here instead of advancing to the first component's ARCHITECT.  This is
    # the mechanism used by component-level regression tests to isolate the
    # decompose step: capture the initial state with stop-after=true in the
    # TOP task.json, run the orchestrator, verify it stops here.
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


def _run_tester_internal(job_doc: Path) -> AgentResult:
    """Run the test command from task.json and return pass/fail as a structured result."""
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


def _run_documenter_internal(job_doc: Path, output_dir: Path) -> AgentResult:
    """Scan output_dir for *.md files and rebuild README.md with a documentation index.

    Reads documents_written from task.json; returns DOCUMENTER_DONE immediately
    (no-op) if the field is false or absent.
    """
    task_json_path = job_doc.parent / "task.json"
    documents_written = False
    if task_json_path.exists():
        try:
            documents_written = json.loads(task_json_path.read_text()).get("documents_written", False)
        except Exception:
            pass

    if not documents_written:
        return AgentResult(exit_code=0, response="OUTCOME: DOCUMENTER_DONE\nHANDOFF: documents_written=false; skipped")

    design_docs: list[tuple[str, str]] = []
    impl_docs:   list[tuple[str, str]] = []

    for md_file in sorted(output_dir.glob("*.md")):
        if md_file.name == "README.md":
            continue
        content = md_file.read_text()

        purpose = ""
        m = re.search(r'[Pp]urpose[:\s]+([^\n.]+\.?)', content)
        if m:
            purpose = m.group(1).strip().rstrip('.')

        tags: list[str] = []
        m = re.search(r'[Tt]ags[:\s]+([^\n]+)', content)
        if m:
            tags = [t.strip() for t in m.group(1).split(',')]

        entry = (md_file.name, purpose)
        if "implementation" in tags:
            impl_docs.append(entry)
        else:
            design_docs.append(entry)

    if not design_docs and not impl_docs:
        return AgentResult(exit_code=0, response="OUTCOME: DOCUMENTER_DONE\nHANDOFF: no .md files found to index")

    lines: list[str] = ["## Documentation", ""]
    if design_docs:
        lines += ["### Design", "| File | Description |", "|------|-------------|"]
        for name, desc in design_docs:
            lines.append(f"| {name} | {desc} |")
        lines.append("")
    if impl_docs:
        lines += ["### Implementation Notes", "| File | Description |", "|------|-------------|"]
        for name, desc in impl_docs:
            lines.append(f"| {name} | {desc} |")
        lines.append("")

    doc_section = "\n".join(lines)

    readme_path = output_dir / "README.md"
    if readme_path.exists():
        readme = readme_path.read_text()
        if "## Documentation" in readme:
            readme = re.sub(r'## Documentation.*?(?=\n## |\Z)', doc_section + "\n", readme, flags=re.DOTALL)
        else:
            readme = readme.rstrip() + "\n\n" + doc_section + "\n"
    else:
        readme = f"# Documentation\n\n{doc_section}\n"
    readme_path.write_text(readme)

    n = len(design_docs) + len(impl_docs)
    return AgentResult(
        exit_code=0,
        response=(
            f"OUTCOME: DOCUMENTER_DONE\n"
            f"HANDOFF: indexed {n} doc(s) into README.md "
            f"({len(design_docs)} design, {len(impl_docs)} implementation)"
        ),
    )


def _run_lch_internal(run_dir: Path) -> AgentResult:
    """Execute LEAF_COMPLETE_HANDLER logic directly without a claude subprocess.

    Runs on-task-complete.sh and maps its three possible outputs to the
    corresponding outcome strings. No AI reasoning is required for this role.

    run_dir is passed as --output-dir to on-task-complete.sh so that
    set-current-job.sh writes current-job.txt to the correct coordination dir.
    """
    current_job_path = CURRENT_JOB_FILE.read_text().strip()
    cmd = [
        str(PM_SCRIPTS_DIR / "on-task-complete.sh"),
        "--current", current_job_path,
        "--output-dir", str(run_dir),
        "--epic", EPIC,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    stdout = proc.stdout.strip()

    if proc.returncode != 0:
        err = proc.stderr.strip() or stdout
        print(f"[internal/LCH] on-task-complete.sh failed (exit {proc.returncode}): {err}")
        return AgentResult(exit_code=1, response=f"on-task-complete.sh failed: {err}")

    # on-task-complete.sh may emit status lines before the terminal token.
    # Scan each line for NEXT/DONE/STOP_AFTER and the optional TOP_RENAME_PENDING
    # token (emitted when the top-level build directory rename is deferred).
    outcome = None
    token_line = ""
    top_rename_pending = None
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line.startswith("TOP_RENAME_PENDING "):
            # advance-pipeline.sh deferred the top-level rename so the orchestrator
            # can flush metrics to task.json while paths are still valid. Capture
            # the directory to rename; the orchestrator applies it after all writes.
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


def _save_handoff_state(output_dir: Path, handoff_history: list[str], frame_stack: list[dict]) -> None:
    """Write handoff_history and frame_stack to handoff-state.json in output_dir."""
    state = {
        "handoff_history": handoff_history,
        "frame_stack": frame_stack,
    }
    try:
        (output_dir / "handoff-state.json").write_text(json.dumps(state, indent=2) + "\n")
    except Exception as e:
        print(f"[orchestrator] Warning: failed to save handoff state: {e}")


def _load_handoff_state(path: Path) -> tuple[list[str], list[dict]]:
    """Load handoff_history and frame_stack from a JSON file.

    Returns (handoff_history, frame_stack) — empty lists if the file cannot
    be read or is missing required keys.
    """
    try:
        data = json.loads(path.read_text())
        history = data.get("handoff_history", [])
        stack = data.get("frame_stack", [])
        if not isinstance(history, list) or not isinstance(stack, list):
            print(f"[orchestrator] Warning: handoff state file has unexpected shape: {path}")
            return [], []
        return history, stack
    except Exception as e:
        print(f"[orchestrator] Warning: failed to load handoff state from {path}: {e}")
        return [], []


def _store_architect_design_fields(response: str, job_doc: Path) -> None:
    """Parse design fields from ARCHITECT's response, update task_state, and
    persist to task.json.

    Tries XML <response> block first, falls back to terminal ```json block.
    Updates in-memory task_state first so downstream stages (IMPLEMENTOR,
    TESTER) can read values without a disk round-trip. task.json write is for
    persistence/resume only.
    """
    fields: dict = {}

    xml_match = re.search(r'<response>(.*?)</response>', response, re.DOTALL)
    if xml_match:
        block = xml_match.group(0)
        for key in ("design", "acceptance_criteria", "test_command"):
            val = _extract_xml_tag(block, key)
            if val:
                fields[key] = val
        dw = _extract_xml_tag(block, "documents_written")
        if dw:
            fields["documents_written"] = dw.lower() == "true"
    else:
        json_match = re.search(r'```json\s*\n(\{.*?\})\s*```\s*$', response, re.DOTALL)
        if not json_match:
            return
        try:
            data = json.loads(json_match.group(1))
        except json.JSONDecodeError:
            return
        fields = {k: data[k] for k in ("design", "acceptance_criteria", "test_command", "documents_written") if k in data}

    if not fields:
        return

    # Update in-memory state first
    _update_task_state(fields)

    # Persist to task.json (resume/debug only)
    task_json_path = job_doc.parent / "task.json"
    if not task_json_path.exists():
        return
    try:
        tj = json.loads(task_json_path.read_text())
        tj.update(fields)
        task_json_path.write_text(json.dumps(tj, indent=2) + "\n")
    except Exception as e:
        print(f"[orchestrator] Warning: failed to persist design fields to task.json: {e}")


def _lch_two_phase_pop(frame_stack: list[dict], handoff_history: list[str], completed_job_doc: Path | None) -> None:
    """Two-phase frame pop executed after each TESTER pass (via LCH).

    Phase 1: always pop the component frame, truncate history to anchor,
    append '{component} complete' entry with the component's output_dir.

    Phase 2: if the completed task had last-task=true, also pop the decompose
    frame, truncate further, and append a level summary.
    """
    completed_task_data: dict = {}
    if completed_job_doc:
        tj = completed_job_doc.parent / "task.json"
        if tj.exists():
            try:
                completed_task_data = json.loads(tj.read_text())
            except Exception:
                pass

    # Phase 1: pop component frame
    if frame_stack and frame_stack[-1].get("type") == "component":
        frame = frame_stack.pop()
        anchor = frame["anchor_index"]
        handoff_history[:] = handoff_history[:anchor + 1]
        comp_name = frame["component_name"]
        output_dir_str = completed_task_data.get("output_dir", "")
        handoff_history.append(f"[{comp_name} complete] {output_dir_str}")

    # Phase 2: if last component, pop decompose frame and emit level summary
    if completed_task_data.get("last-task"):
        if frame_stack and frame_stack[-1].get("type") == "decompose":
            frame = frame_stack.pop()
            anchor = frame["anchor_index"]
            # Collect component completion entries from this level
            level_summaries = " | ".join(
                e for e in handoff_history[anchor + 1:]
                if e.startswith("[") and "complete" in e
            )
            handoff_history[:] = handoff_history[:anchor + 1]
            parent_name = completed_job_doc.parent.parent.name if completed_job_doc else "level"
            handoff_history.append(f"[{parent_name} complete] {level_summaries}")


def run_internal_agent(role: str, output_dir: Path, job_doc: Path | None, components: list[dict] | None = None) -> AgentResult:
    """Dispatch to the internal implementation for the given role."""
    if role == "LEAF_COMPLETE_HANDLER":
        # LCH uses RUN_DIR (where current-job.txt lives), not the per-component
        # subdirectory that task_output_dir may point to.
        return _run_lch_internal(RUN_DIR)
    if role == "DECOMPOSE_HANDLER":
        if job_doc is None:
            return AgentResult(exit_code=1, response="DECOMPOSE_HANDLER requires a job_doc")
        if not components:
            return AgentResult(exit_code=1, response="DECOMPOSE_HANDLER requires components from ARCHITECT JSON response")
        return _run_decompose_internal(job_doc, components)
    if role in ("DOCUMENTER_POST_ARCHITECT", "DOCUMENTER_POST_IMPLEMENTOR"):
        if job_doc is None:
            return AgentResult(exit_code=1, response=f"{role} requires a job_doc")
        return _run_documenter_internal(job_doc, output_dir)
    if role == "TESTER":
        if job_doc is None:
            return AgentResult(exit_code=1, response="TESTER requires a job_doc")
        return _run_tester_internal(job_doc)
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
    "runs", "current-job.txt", "last-job.json", "execution.log",
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

# ---------------------------------------------------------------------------
# Loop detection
#
# A sliding window of (role, job_doc_path) pairs for recent invocations.
# Any repeat within the window means a handler failed to advance the pipeline.
# Window size of 8 is enough to catch ARCHITECT → DECOMPOSE_HANDLER → ARCHITECT
# cycles with headroom for deeper nesting.
# ---------------------------------------------------------------------------

_LOOP_WINDOW_SIZE = 8
_loop_window: list[tuple[str, str]] = []

# ---------------------------------------------------------------------------
# In-memory task state cache
#
# task.json is the persistence layer (written on every state transition so a
# resume can restore state). During normal operation the orchestrator passes
# state between stages from this dict — never by re-reading task.json from
# disk. task.json is read from disk only:
#   1. When job_doc is first set or advanced (populates the cache)
#   2. On --resume (restores the cache after an interrupted run)
# ---------------------------------------------------------------------------

task_state: dict = {}  # fields for the current job_doc


def _load_task_state(jd: Path | None) -> None:
    """Load task.json for jd into task_state. No-op if jd is None or missing."""
    global task_state
    if jd is None:
        return
    tj_path = jd.parent / "task.json"
    try:
        task_state = json.loads(tj_path.read_text())
    except Exception:
        task_state = {}


def _update_task_state(fields: dict) -> None:
    """Merge fields into task_state (in-memory only — caller handles disk write)."""
    task_state.update(fields)


current_role = _start_state
job_doc      = initial_job_doc
_load_task_state(job_doc)
handoff_history: list[str] = []
# Frame stack for scope-bounded handoff history. Two frame types:
#   {"type": "decompose", "anchor_index": N}
#       Pushed by DECOMPOSE_HANDLER; popped by LCH when last-task=true.
#   {"type": "component", "anchor_index": N, "component_name": X}
#       Pushed just before ARCHITECT runs in atomic/design mode; popped by LCH
#       after every TESTER pass.
frame_stack: list[dict] = []

# Pre-populate handoff state if --handoff-file provided or --resume + auto-load.
_handoff_load_path: Path | None = None
if args.handoff_file:
    _handoff_load_path = args.handoff_file
elif args.resume and HANDOFF_STATE_FILE.exists():
    _handoff_load_path = HANDOFF_STATE_FILE
if _handoff_load_path:
    _loaded_history, _loaded_stack = _load_handoff_state(_handoff_load_path)
    handoff_history.extend(_loaded_history)
    frame_stack.extend(_loaded_stack)
    print(f"[orchestrator] Loaded handoff state from {_handoff_load_path} "
          f"({len(handoff_history)} history entries, {len(frame_stack)} frame(s))")

    # Stale component frame detection: if the top frame is a component frame
    # and the component's task.json doesn't have complete:true, the previous run
    # did not finish this component cleanly (NEED_HELP or interrupt).
    # Recovery: pop the frame and truncate handoff_history to the pre-component
    # anchor so the resumed ARCHITECT sees clean context.
    #
    # Note: complete:true is not yet written to task.json; the check always
    # treats a component frame as stale, which is the safe default.
    if frame_stack and frame_stack[-1].get("type") == "component":
        _stale_frame = frame_stack[-1]
        _comp_name = _stale_frame["component_name"]
        _is_complete = False
        if initial_job_doc:
            _comp_tj = initial_job_doc.parent / "task.json"
            if _comp_tj.exists():
                try:
                    _is_complete = json.loads(_comp_tj.read_text()).get("complete", False)
                except Exception:
                    pass
        if not _is_complete:
            frame_stack.pop()
            handoff_history[:] = handoff_history[:_stale_frame["anchor_index"] + 1]
            print(f"[orchestrator] WARNING: stale component frame detected for '{_comp_name}'.")
            print(f"    The previous run did not complete this component cleanly (NEED_HELP or interrupt).")
            print(f"    Truncating handoff history to the pre-component anchor and retrying.")
role_iteration_counts: dict[str, int] = {}
role_counters: dict[str, int] = {}

# Metrics state
_task_name = description_from_job_path(initial_job_doc) if initial_job_doc else "pipeline"
run = RunData(task_name=_task_name, start=datetime.now())
build_readme: Path | None = None      # Level:TOP pipeline-subtask README for live log
top_task_json: Path | None = None     # Level:TOP task.json — target for metrics persistence
_resume_log_seeded = False            # guard: seed prior log at most once per run


def _seed_run_from_prior_log(task_json: Path) -> None:
    """On resume, pre-populate run.invocations from the existing execution_log
    in task.json, then append a RESUME sentinel so the history is auditable.

    Sets run.start to the original run's start time so elapsed totals in
    run_summary remain meaningful.
    """
    global _resume_log_seeded
    if _resume_log_seeded:
        return
    _resume_log_seeded = True

    try:
        data = json.loads(task_json.read_text())
    except Exception:
        return

    prior = data.get("execution_log", [])
    if not prior:
        return

    for entry in prior:
        try:
            inv = InvocationRecord(
                role=entry["role"],
                agent=entry["agent"],
                n=entry["n"],
                description=entry["description"],
                start=datetime.fromisoformat(entry["start"]),
                end=datetime.fromisoformat(entry["end"]),
                elapsed=timedelta(seconds=entry["elapsed_s"]),
                tokens_in=entry["tokens_in"],
                tokens_out=entry["tokens_out"],
                tokens_cached=entry["tokens_cached"],
                outcome=entry["outcome"],
            )
            run.invocations.append(inv)
        except Exception:
            continue

    # Reset run start to match the original run's start time
    if run.invocations:
        run.start = run.invocations[0].start

    # Append RESUME sentinel
    now = datetime.now()
    sentinel = InvocationRecord(
        role="RESUME",
        agent="orchestrator",
        n=0,
        description="pipeline resumed",
        start=now,
        end=now,
        elapsed=timedelta(0),
        tokens_in=0,
        tokens_out=0,
        tokens_cached=0,
        outcome="RESUME",
    )
    run.invocations.append(sentinel)
    print(f"[orchestrator] Resume: loaded {len(prior)} prior invocations from execution log.")


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
top_task_json = build_readme.parent / "task.json" if build_readme else None

# On resume, seed run.invocations from the prior execution log (if available now)
if args.resume and top_task_json is not None and top_task_json.exists():
    _seed_run_from_prior_log(top_task_json)

# In TM mode, ensure the TOP task's task.json has output_dir set.
if TM_MODE and initial_job_doc:
    _top_tj = initial_job_doc.parent / "task.json"
    if _top_tj.exists():
        try:
            _top_data = json.loads(_top_tj.read_text())
            if "output_dir" not in _top_data:
                _top_data["output_dir"] = str(OUTPUT_DIR)
                _top_tj.write_text(json.dumps(_top_data, indent=2) + "\n")
        except Exception:
            pass

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
if RUN_DIR != OUTPUT_DIR:
    print(f"    run dir:       {RUN_DIR}")
print(f"    execution log: {EXECUTION_LOG}\n")

last_components: list[dict] = []  # components from most recent ARCHITECT JSON response

# Deferred top-level rename: set when advance-pipeline.sh emits TOP_RENAME_PENDING.
# The orchestrator renames build-N → X-build-N only AFTER all metrics/README writes
# complete, keeping task.json paths valid for the entire post-loop flush sequence.
_pending_top_rename: Path | None = None

# Register handoff state save on every exit (clean, sys.exit, KeyboardInterrupt).
atexit.register(lambda: _save_handoff_state(RUN_DIR, handoff_history, frame_stack))

while current_role is not None:
    agent = AGENTS.get(current_role)
    if agent is None:
        print(f"[orchestrator] No agent configured for role {current_role}. Halting.")
        sys.exit(1)

    # Derive per-task output dir from in-memory task_state (falls back to OUTPUT_DIR)
    task_output_dir = OUTPUT_DIR
    if job_doc and TM_MODE:
        if "output_dir" in task_state:
            task_output_dir = Path(task_state["output_dir"])

    print(f"\n>>> [{current_role} / {agent}]")

    # Push component frame just before ARCHITECT runs in atomic/design mode.
    # This frame is popped by LCH after each TESTER pass.
    if current_role == "ARCHITECT" and TM_MODE and job_doc:
        if task_state.get("complexity") == "atomic":
            frame_stack.append({
                "type": "component",
                "anchor_index": len(handoff_history) - 1,
                "component_name": task_state.get("name", job_doc.parent.name),
            })

    # If DECOMPOSE_HANDLER is starting without components (e.g. --start-state resume),
    # load them from task_state (already populated from task.json at job_doc advance).
    if current_role == "DECOMPOSE_HANDLER" and not last_components and job_doc:
        last_components = task_state.get("components", [])

    # Loop detection: for handler roles only — same (role, job_doc) in the
    # sliding window means the handler failed to advance current-job.txt.
    # AI agent roles (ARCHITECT, IMPLEMENTOR) can legitimately revisit the same
    # task via TESTER_TESTS_FAIL→IMPLEMENTOR or ARCHITECT_NEEDS_REVISION retries.
    _HANDLER_ROLES = {"DECOMPOSE_HANDLER", "LEAF_COMPLETE_HANDLER"}
    _loop_key = (current_role, str(job_doc) if job_doc else "")
    if current_role in _HANDLER_ROLES and _loop_key in _loop_window:
        _cycle_len = len(_loop_window) - _loop_window.index(_loop_key)
        _desc = description_from_job_path(job_doc)
        print(f"\n[orchestrator] ERROR: pipeline loop detected — "
              f"{current_role}/{_desc} already ran {_cycle_len} iteration(s) ago. "
              f"A handler did not advance current-job.txt. Halting.")
        if job_doc:
            print(f"    Job document: {job_doc}")
        sys.exit(1)
    _loop_window.append(_loop_key)
    if len(_loop_window) > _LOOP_WINDOW_SIZE:
        _loop_window.pop(0)

    inv_start = datetime.now()
    if agent == "internal":
        result: AgentResult = run_internal_agent(current_role, task_output_dir, job_doc,
                                                  last_components if current_role == "DECOMPOSE_HANDLER" else None)
    else:
        prompt = build_prompt(current_role, job_doc, task_output_dir, handoff_history, agent)
        result = run_agent(agent, TIMEOUT_MINUTES, current_role, prompt, OUTPUT_DIR)
    inv_end = datetime.now()

    if result.exit_code == 2:
        print(f"\n[orchestrator] {current_role} timed out. Halting.")
        sys.exit(1)
    if result.exit_code == 1:
        print(f"\n[orchestrator] {current_role} agent error. Halting.")
        sys.exit(1)

    outcome, handoff, last_components = parse_response(result.response)
    handoff_history.append(f"[{current_role}] {handoff}")
    log_run(current_role, agent, outcome, handoff)

    # Store ARCHITECT design fields in task.json so IMPLEMENTOR/TESTER can
    # read them without a file dependency on the job doc.
    if outcome == "ARCHITECT_DESIGN_READY" and job_doc:
        _store_architect_design_fields(result.response, job_doc)

    # Store components in task_state and persist to task.json for resume.
    if outcome == "ARCHITECT_DECOMPOSITION_READY" and last_components and job_doc:
        _update_task_state({"components": last_components})
        _tj_path = job_doc.parent / "task.json"
        if _tj_path.exists():
            try:
                _tj = json.loads(_tj_path.read_text())
                _tj["components"] = last_components
                _tj_path.write_text(json.dumps(_tj, indent=2) + "\n")
            except Exception as e:
                print(f"[orchestrator] Warning: failed to persist components to task.json: {e}")

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

    # Persist execution_log to TOP-level task.json after every invocation
    if top_task_json is None and job_doc is not None:
        _top = _find_level_top(job_doc)
        if _top is not None:
            top_task_json = _top.parent / "task.json"
            # Lazy resume seed: top_task_json just resolved for the first time
            if args.resume:
                _seed_run_from_prior_log(top_task_json)
    metrics_mod.write_metrics_to_task_json(top_task_json, run)

    # Re-render the TOP-level README after every invocation (live progress)
    if top_task_json is not None:
        render_task_readme(top_task_json)

    # Re-render the active task README if it differs from the TOP-level one
    if job_doc is not None:
        active_task_json = job_doc.parent / "task.json"
        if active_task_json != top_task_json and active_task_json.exists():
            render_task_readme(active_task_json)

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

    # Validate outcome is a recognised transition FROM the current role.
    # Checking against all routes (any role) is insufficient — it allows an agent
    # to emit another role's outcome and silently mis-route the pipeline.
    valid_for_role = [o for (r, o) in ROUTES if r == current_role]
    if outcome not in valid_for_role:
        all_known = [o for (_, o) in ROUTES]
        if outcome in all_known:
            print(f"\n[orchestrator] Invalid outcome '{outcome}' from {current_role} "
                  f"(belongs to a different role). Halting.")
        else:
            print(f"\n[orchestrator] Unrecognised outcome '{outcome}' from {current_role}. Halting.")
        sys.exit(1)

    # After a handler signals HANDLER_SUBTASKS_READY, read the current job path for downstream agents.
    # DECOMPOSE: push a decompose frame BEFORE job_doc is updated.
    # LEAF:      two-phase pop AFTER job_doc is updated.
    if current_role in ("DECOMPOSE_HANDLER", "LEAF_COMPLETE_HANDLER") and outcome == "HANDLER_SUBTASKS_READY":
        if not CURRENT_JOB_FILE.exists():
            print(f"\n[orchestrator] Handler did not write job path to {CURRENT_JOB_FILE}. Halting.")
            sys.exit(1)

        if current_role == "DECOMPOSE_HANDLER" and job_doc:
            frame_stack.append({
                "type": "decompose",
                "anchor_index": len(handoff_history) - 1,
            })

        old_job_doc = job_doc
        # Read current-job.txt once — written by the handler subprocess as its
        # output mechanism. Persistence/resume only; not a re-read of known state.
        job_doc = Path(CURRENT_JOB_FILE.read_text().strip())
        if not job_doc.exists():
            print(f"\n[orchestrator] Job document not found: {job_doc}. Halting.")
            sys.exit(1)
        print(f"    current job:   {job_doc}")
        _load_task_state(job_doc)  # populate in-memory state for the new job
        LAST_JOB_FILE.write_text(json.dumps({"active_task": str(job_doc.parent / "task.json")}, indent=2) + "\n")
        if build_readme is None:
            build_readme = _find_level_top(job_doc)

        if current_role == "LEAF_COMPLETE_HANDLER":
            _lch_two_phase_pop(frame_stack, handoff_history, old_job_doc)

    # Pipeline fully done: still need the two-phase pop for the last component.
    if current_role == "LEAF_COMPLETE_HANDLER" and outcome == "HANDLER_ALL_DONE":
        _lch_two_phase_pop(frame_stack, handoff_history, job_doc)
        # Capture any deferred top-level rename from advance-pipeline.sh.
        # The rename will be applied AFTER all post-loop metrics/README writes.
        _m = re.search(r'^TOP_RENAME_PENDING: (.+)$', result.response, re.MULTILINE)
        if _m:
            _pending_top_rename = Path(_m.group(1).strip())

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

# 1. Metrics — write run_summary + execution_log to TOP-level task.json
# NOTE: top_task_json is still valid here because advance-pipeline.sh deferred
# the build-N → X-build-N rename (via TOP_RENAME_PENDING protocol). The rename
# happens below, as the very last step, so all writes below use valid paths.
metrics_mod.write_metrics_to_task_json(top_task_json, run, final=True)
metrics_mod.write_summary_to_readme(build_readme, run)

# 2. README render — final render with complete run_summary now in task.json
if top_task_json is not None:
    render_task_readme(top_task_json)

# 3. Master index — rebuild combined doc index across the output tree
build_master_index(OUTPUT_DIR)

# 4. Apply deferred top-level rename (build-N → X-build-N).
# This is the last step so that all in-memory paths remain valid for the
# writes above. advance-pipeline.sh deferred the rename via TOP_RENAME_PENDING.
if _pending_top_rename is not None and _pending_top_rename.exists():
    _renamed_dir = _pending_top_rename.parent / ("X-" + _pending_top_rename.name)
    _pending_top_rename.rename(_renamed_dir)
    print(f"    renamed:       {_pending_top_rename.name} → {_renamed_dir.name}")

print("\n=== Orchestrator: pipeline complete ===")
