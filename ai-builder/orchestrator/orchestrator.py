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
from agents.builder.tester import TesterAgent
from agents.builder.documenter import DocumenterAgent
from agents.builder.decompose import DecomposeAgent
from agents.builder.lch import LCHAgent
from agents.context import AgentContext
from agents.loader import load_internal_agent
from gemini_compat import gemini_role_addendum
import metrics as metrics_mod
from metrics import RunData, InvocationRecord, description_from_job_path
from render_readme import render_task_readme
from build_master_index import build_master_index
import recorder as recorder_mod


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
parser.add_argument(
    "--halt-after-ai-invocation",
    type=int,
    metavar="N",
    help="Halt cleanly after the Nth AI invocation (ARCHITECT/IMPLEMENTOR/TESTER). "
         "Non-AI handlers for that cycle complete first; current-job.txt is advanced "
         "before halting. Used for deterministic resume testing.",
)
parser.add_argument(
    "--record-to",
    type=Path,
    metavar="DIR",
    help="Record mode: commit the regression workspace to a git repo in DIR after "
         "every invocation and write a recording.json manifest at run end. DIR should "
         "be the regression workspace root containing both output/ and target/.",
)
parser.add_argument(
    "--record-branch",
    metavar="BRANCH",
    help="Orphan branch name for the recording repo (e.g. 'user-service'). "
         "Used with --record-to when initializing a new recording repo.",
)
parser.add_argument(
    "--record-remote",
    metavar="URL",
    help="Remote URL to add as 'origin' in the recording repo (e.g. the "
         "ai-builder-recordings GitHub repo). Used with --record-to.",
)
parser.add_argument(
    "--replay-from",
    type=Path,
    metavar="DIR",
    help="Replay mode: serve pre-recorded AI responses from DIR instead of calling "
         "the AI. Non-AI handlers re-run normally. Checks for prompt drift at startup "
         "and aborts if prompts have changed since the recording was captured.",
)
parser.add_argument(
    "--ignore-prompt-drift",
    action="store_true",
    help="In replay mode, continue even if role prompts have changed since the "
         "recording was captured (prints a warning instead of aborting).",
)
args = parser.parse_args()

if args.record_to and args.replay_from:
    print("[orchestrator] --record-to and --replay-from are mutually exclusive.")
    sys.exit(1)

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
ROLES_DIR       = REPO_ROOT / "ai-builder" / "orchestrator" / "machines" / "builder" / "roles"
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
        # Override start_state with the role that was active when interrupted,
        # if it was persisted to task.json.
        try:
            _resume_tj = initial_job_doc.parent / "task.json"
            if _resume_tj.exists():
                _resume_role = json.loads(_resume_tj.read_text()).get("active_role")
                if _resume_role:
                    _start_state = _resume_role
                    print(f"[orchestrator] Resume: restoring active role '{_resume_role}' from task.json")
        except Exception as e:
            print(f"[orchestrator] Warning: could not read active_role from task.json on resume: {e}")
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

# Build the AgentContext used by internal agents that need orchestrator-level
# constants. TARGET_REPO / PM_SCRIPTS_DIR / EPIC are only set in TM mode;
# agents that require them (DecomposeAgent, LCHAgent) are only invoked in
# TM mode, so the None defaults are never reached in practice.
_agent_ctx = AgentContext(
    run_dir          = RUN_DIR,
    current_job_file = CURRENT_JOB_FILE,
    pm_scripts_dir   = PM_SCRIPTS_DIR if TM_MODE else Path("."),
    epic             = EPIC if TM_MODE else "",
    output_dir       = OUTPUT_DIR,
    target_repo      = TARGET_REPO if TM_MODE else None,
)


# ---------------------------------------------------------------------------
# State machine loader
# ---------------------------------------------------------------------------

def load_state_machine(machine_file: Path) -> tuple[dict, dict, str, dict, set[str], dict]:
    """Load and validate a machine JSON file.

    Returns (agents, routes, start_state, role_prompts, no_history_roles, role_configs) where:
      agents           — maps role name → agent CLI name
      routes           — maps (role, outcome) → next role or None
      start_state      — default entry role
      role_prompts     — maps role → Path (prompt file) or None (dynamic generation)
      no_history_roles — set of roles that receive no handoff history in their prompt
      role_configs     — maps role name → full config dict from machine JSON
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

    return agents, routes, start_state, role_prompts, no_history_roles, roles


# ---------------------------------------------------------------------------
# Pipeline config — load state machine
# ---------------------------------------------------------------------------

if args.state_machine:
    _machine_file = args.state_machine.resolve()
    if not _machine_file.exists():
        print(f"[orchestrator] Machine file not found: {_machine_file}")
        sys.exit(1)
elif TM_MODE:
    _machine_file = MACHINES_DIR / "builder" / "default.json"
else:
    _machine_file = MACHINES_DIR / "builder" / "simple.json"

AGENTS, ROUTES, _start_state, ROLE_PROMPTS, NO_HISTORY_ROLES, ROLE_CONFIGS = load_state_machine(_machine_file)

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
    if role == "ACCEPTANCE_SPEC_WRITER":
        valid_outcomes = "ACCEPTANCE_SPEC_WRITER_DONE | ACCEPTANCE_SPEC_WRITER_UNSUPPORTED_INTERFACE"
        job_section = (
            f"\nThe shared job document is at: {job_doc}\n"
            f"\nOutput directory (write both output files here): {output_dir}\n"
        )
    elif role == "ARCHITECT":
        # Read complexity, level, goal, context from in-memory task_state.
        # task.json was loaded into task_state when job_doc was last set —
        # no disk read needed here. Falls back gracefully for edge cases.
        # See: learning/pipeline-extract-dont-delegate.md (Gemini cwd isolation)
        complexity    = task_state.get("complexity", "—")
        level         = task_state.get("level", "TOP")
        goal_text     = task_state.get("goal", "")
        context_text  = task_state.get("context", "")
        component_name = task_state.get("name", "")
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
        name_line = f"Component Name: {component_name}\n" if component_name else ""
        job_section = (
            f"\nThe shared job document is at: {job_doc}\n"
            f"Task Level: {level}\n"
            f"Complexity: {complexity}\n"
            f"{name_line}"
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
        route_on = ROLE_CONFIGS.get(role, {}).get("route_on")
        return LCHAgent(ctx=_agent_ctx, route_on=route_on).run(job_doc or Path("."), output_dir)
    if role == "DECOMPOSE_HANDLER":
        if job_doc is None:
            return AgentResult(exit_code=1, response="DECOMPOSE_HANDLER requires a job_doc")
        if not components:
            return AgentResult(exit_code=1, response="DECOMPOSE_HANDLER requires components from ARCHITECT JSON response")
        return DecomposeAgent(ctx=_agent_ctx).run(job_doc, output_dir, components=components)
    if role in ("DOCUMENTER_POST_ARCHITECT", "DOCUMENTER_POST_IMPLEMENTOR"):
        if job_doc is None:
            return AgentResult(exit_code=1, response=f"{role} requires a job_doc")
        return DocumenterAgent().run(job_doc, output_dir)
    if role == "TESTER":
        if job_doc is None:
            return AgentResult(exit_code=1, response="TESTER requires a job_doc")
        return TesterAgent().run(job_doc, output_dir)
    # Generic fallback: resolve impl path from machine JSON and instantiate via loader
    impl_path = ROLE_CONFIGS.get(role, {}).get("impl")
    if impl_path:
        if job_doc is None:
            return AgentResult(exit_code=1, response=f"{role} requires a job_doc")
        agent = load_internal_agent(impl_path, _agent_ctx)
        return agent.run(job_doc, output_dir)
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
    """Return the topmost README (at or above readme's directory) whose task.json has level: TOP.

    Walks upward through all parent directories and returns the highest-level
    match. Walking to the top (not stopping at the first match) ensures that
    decompose-propagated level=TOP values on child tasks do not shadow the real
    Level:TOP build-N entry point when resuming from a mid-tree task.
    """
    if not readme:
        return None
    candidate = readme
    result = None
    while candidate and candidate.exists():
        task_json = candidate.parent / "task.json"
        if task_json.exists():
            try:
                data = json.loads(task_json.read_text())
                if data.get("level") == "TOP":
                    result = candidate  # keep walking; a higher ancestor may also match
            except Exception:
                pass
        parent_readme = candidate.parent.parent / "README.md"
        if parent_readme == candidate:
            break
        candidate = parent_readme
    return result

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
ai_invocation_count = 0           # counts completed AI-role invocations (excludes handlers)

# Recording state
record_dir: Path | None = args.record_to.resolve() if args.record_to else None
_rec_n = 0                        # total invocation counter (AI + handlers) for commit sequence
_rec_invocations: list[dict] = [] # manifest invocation list built during the run

if record_dir is not None:
    recorder_mod.init(record_dir, branch=args.record_branch, remote_url=args.record_remote)

# Replay state
replay_dir: Path | None = args.replay_from.resolve() if args.replay_from else None
_replay_ai_queue: list[tuple[int, str, str]] = []  # (n, role, response_text) for AI invocations
_replay_ai_idx = 0                                  # index into _replay_ai_queue

if replay_dir is not None:
    _replay_manifest = recorder_mod.load_manifest(replay_dir)
    _drift = recorder_mod.check_prompt_drift(_replay_manifest, ROLE_PROMPTS, REPO_ROOT)
    if _drift and not args.ignore_prompt_drift:
        print("[orchestrator] Prompt drift detected — these prompts changed since recording:")
        for _d in _drift:
            print(f"    {_d}")
        print("[orchestrator] Use --ignore-prompt-drift to replay anyway.")
        sys.exit(1)
    elif _drift:
        print("[orchestrator] WARNING: prompt drift detected (--ignore-prompt-drift). Continuing.")
        for _d in _drift:
            print(f"    {_d}")
    _replay_ai_queue = recorder_mod.load_ai_responses(replay_dir, _replay_manifest)
    print(f"[orchestrator] Replay mode: {len(_replay_ai_queue)} AI invocation(s) queued from {replay_dir}")

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

    # Persist active_role to task.json so --resume can restart from this role
    # rather than always re-entering from start_state.
    if job_doc:
        _active_tj = job_doc.parent / "task.json"
        if _active_tj.exists():
            try:
                _tj_data = json.loads(_active_tj.read_text())
                _tj_data["active_role"] = current_role
                _active_tj.write_text(json.dumps(_tj_data, indent=2) + "\n")
            except Exception as e:
                print(f"[orchestrator] Warning: could not persist active_role to task.json: {e}")

    # Halt after N AI invocations (--halt-after-ai-invocation). Fires just before
    # the (N+1)th AI role — after all handlers from the Nth cycle have completed
    # and current-job.txt is already advanced to the next task.
    if (agent != "internal"
            and args.halt_after_ai_invocation is not None
            and ai_invocation_count >= args.halt_after_ai_invocation):
        print(f"\n[orchestrator] Halting after {ai_invocation_count} AI invocation(s) "
              f"(--halt-after-ai-invocation {args.halt_after_ai_invocation}).")
        sys.exit(0)

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
    elif replay_dir is not None:
        # Replay mode: serve the next pre-recorded response instead of calling the AI.
        if _replay_ai_idx >= len(_replay_ai_queue):
            print(f"\n[orchestrator] Replay exhausted: no recorded response for {current_role} "
                  f"(used all {len(_replay_ai_queue)} queued response(s)).")
            sys.exit(1)
        _rep_n, _rep_role, _rep_response = _replay_ai_queue[_replay_ai_idx]
        if _rep_role != current_role:
            print(f"\n[orchestrator] Replay role mismatch at queue index {_replay_ai_idx}: "
                  f"recording expected {_rep_role}, orchestrator dispatched {current_role}. "
                  f"Routing has diverged from the recording.")
            sys.exit(1)
        print(f"[orchestrator] Replaying inv-{_rep_n:02d} {current_role} (pre-recorded)")
        result = AgentResult(exit_code=0, response=_rep_response)
        _replay_ai_idx += 1
        ai_invocation_count += 1
        # Restore output/ from the recording snapshot so subsequent handlers
        # see the files the AI actually wrote. Skip for ARCHITECT — it writes
        # to target/ via orchestrator-side parsing, not to output/.
        # Exclude orchestrator coordination files so live-run state (paths
        # with the current hex IDs) is not overwritten with recording-era values.
        if current_role != "ARCHITECT":
            recorder_mod.restore_output(replay_dir, _rep_n, exclude=[
                "output/current-job.txt",
                "output/last-job.json",
                "output/execution.log",
                "output/handoff-state.json",
                "output/logs",
            ])
    else:
        prompt = build_prompt(current_role, job_doc, task_output_dir, handoff_history, agent)
        result = run_agent(agent, TIMEOUT_MINUTES, current_role, prompt, OUTPUT_DIR)
        ai_invocation_count += 1
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

    # After LEAF_COMPLETE_HANDLER, re-render all INTERNAL task READMEs.
    # complete-task.sh updates their task.json (via json_complete_subtask)
    # but does not re-render the README. Walk the TOP subtree so every
    # INTERNAL README reflects the latest subtask completion state.
    if current_role == "LEAF_COMPLETE_HANDLER" and top_task_json is not None:
        for _internal_tj in sorted(top_task_json.parent.rglob("task.json")):
            if _internal_tj == top_task_json:
                continue  # TOP is already re-rendered above
            render_task_readme(_internal_tj)

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

    # After a handler signals any "ready" outcome, read the current job path for downstream agents.
    # DECOMPOSE: push a decompose frame BEFORE job_doc is updated.
    # LEAF:      two-phase pop AFTER job_doc is updated.
    # Matches HANDLER_SUBTASKS_READY, HANDLER_INTEGRATE_READY, or any future typed-ready outcomes.
    _is_handler_ready = (
        current_role in ("DECOMPOSE_HANDLER", "LEAF_COMPLETE_HANDLER")
        and outcome.startswith("HANDLER_") and outcome.endswith("_READY")
    )
    if _is_handler_ready:
        if not CURRENT_JOB_FILE.exists():
            print(f"\n[orchestrator] Handler did not write job path to {CURRENT_JOB_FILE}. Halting.")
            sys.exit(1)

        if current_role == "DECOMPOSE_HANDLER" and job_doc and outcome == "HANDLER_SUBTASKS_READY":
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

    # Commit regression workspace snapshot (record mode).
    if record_dir is not None:
        _rec_n += 1
        _sha = recorder_mod.commit(
            record_dir, _rec_n, current_role, outcome,
            response=result.response if agent != "internal" else None,
        )
        _rec_invocations.append({
            "n": _rec_n,
            "role": current_role,
            "outcome": outcome,
            "commit": _sha,
            "ai": agent != "internal",
        })

    next_role = ROUTES.get((current_role, outcome))

    # Record a warning whenever a *_FAIL outcome triggers a retry. This covers
    # linter failures (POST_DOC_HANDLER_ATOMIC_FAIL / INTEGRATE_FAIL → DOC_ARCHITECT
    # / DOC_INTEGRATOR) and tester failures (TESTER_TESTS_FAIL → IMPLEMENTOR).
    # Warnings are written to run_summary in task.json and surfaced in the final
    # run summary so systematic retry rates don't go unnoticed.
    if outcome.endswith("_FAIL") and next_role is not None:
        component = metrics_mod.description_from_job_path(job_doc)
        warning = f"RETRY: {next_role} on {component} (reason: {outcome})"
        run.warnings.append(warning)
        print(f"\n[orchestrator] WARNING: {warning}")

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

# 4. Apply deferred top-level rename (build-N → X-build-N) BEFORE the final
#    recording commit so the commit captures the fully-complete workspace state.
#    All in-memory paths that reference the pre-rename directory are no longer
#    needed at this point (metrics/README writes above are done).
if _pending_top_rename is not None and _pending_top_rename.exists():
    _renamed_dir = _pending_top_rename.parent / ("X-" + _pending_top_rename.name)
    _pending_top_rename.rename(_renamed_dir)
    print(f"    renamed:       {_pending_top_rename.name} → {_renamed_dir.name}")

# 5. Recording manifest — write after all metrics/README updates AND the
#    top-level rename so the "pipeline done" commit captures the final state.
if record_dir is not None:
    if _rec_invocations:
        _sha = recorder_mod.commit(record_dir, _rec_n + 1, "pipeline", "done")
        _rec_invocations.append({
            "n": _rec_n + 1,
            "role": "pipeline",
            "outcome": "done",
            "commit": _sha,
            "ai": False,
        })
    # Extract the top-level user task hex ID from the initial job doc path:
    # .../in-progress/61857e-user-service/61857e-0000-build-1/README.md
    # user-task dir is two levels up; hex ID is the part before the first '-'.
    _task_hex_id: str | None = None
    if TM_MODE:
        try:
            _user_task_dir = initial_job_doc.parent.parent
            _task_hex_id = _user_task_dir.name.split("-")[0]
        except Exception:
            pass
    recorder_mod.write_manifest(record_dir, _rec_invocations, ROLE_PROMPTS, REPO_ROOT,
                                task_hex_id=_task_hex_id)

print("\n=== Orchestrator: pipeline complete ===")
