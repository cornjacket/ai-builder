import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from agent_wrapper import run_agent, AgentResult


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
args = parser.parse_args()

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
else:
    initial_job_doc = args.job.resolve()


# ---------------------------------------------------------------------------
# State machine loader
# ---------------------------------------------------------------------------

def load_state_machine(machine_file: Path) -> tuple[dict, dict, str, dict]:
    """Load and validate a machine JSON file.

    Returns (agents, routes, start_state, role_prompts) where:
      agents      — maps role name → agent CLI name
      routes      — maps (role, outcome) → next role or None
      start_state — default entry role
      role_prompts — maps role → Path (prompt file) or None (dynamic generation)
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

    routes: dict = {}
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

    return agents, routes, start_state, role_prompts


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

AGENTS, ROUTES, _start_state, ROLE_PROMPTS = load_state_machine(_machine_file)

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
    if handoff_history:
        history_section = "\n\n## Handoff Notes from Previous Agents\n\n" + \
            "\n\n---\n\n".join(handoff_history)

    if role == "DECOMPOSE_HANDLER" and ROLE_PROMPTS.get(role) is None:
        current_job_path = CURRENT_JOB_FILE.read_text().strip() if CURRENT_JOB_FILE.exists() else "<job doc path>"
        role_instructions = f"""\
You are the DECOMPOSE HANDLER for the ai-builder pipeline.

Target repository : {TARGET_REPO}
Epic              : {EPIC}
Current job doc   : {current_job_path}

The ARCHITECT has decomposed a service (ARCHITECT_DECOMPOSITION_READY).
The current job doc is the parent service task README. It contains a completed
Components table in the ## Components section.

Your job:
1. Read the Components table from the current job doc.
   Table format: | Name | Complexity | Description |

   Determine the parent's path relative to in-progress/:
     current job doc path: <TARGET_REPO>/project/tasks/<epic>/in-progress/<rel-path>/README.md
     parent rel path     : <rel-path>   (everything between in-progress/ and /README.md)
   You will need this for --parent below.

2. Read the parent task's Level field from its metadata table (TOP or INTERNAL).

3. For each component row, create a subtask directly in in-progress:
     {PM_SCRIPTS_DIR}/new-pipeline-subtask.sh --epic {EPIC} --folder in-progress --parent <parent-rel-path> --name <component-name>

4. For each created subtask, edit its README to fill in:
   - The ## Goal section: the component's one-line description from the table
   - The ## Context section: the parent service's Goal/Context
   - The Complexity field in the metadata table: value from the Components table

5. For the LAST subtask only (the integration component), also set:
   - The Last-task field in the metadata table to: true
   (Change `| Last-task   | false |` to `| Last-task   | true |`)
   - The Level field to the parent task's Level value read in step 2
   (Change `| Level       | INTERNAL |` to `| Level       | <parent-level> |`)

6. Order subtasks by implementation dependency (foundations first).
   The integration subtask must always be last.

7. Point the pipeline at the first subtask:
     {PM_SCRIPTS_DIR}/set-current-job.sh --output-dir {output_dir} <first-subtask-readme-path>

8. Output OUTCOME: HANDLER_SUBTASKS_READY

Available tools:
  {PM_SCRIPTS_DIR}/new-pipeline-subtask.sh --epic {EPIC} --folder in-progress --parent <parent-rel-path> --name <name>
  {PM_SCRIPTS_DIR}/set-current-job.sh      --output-dir {output_dir} <task-readme-path>
  {PM_SCRIPTS_DIR}/list-tasks.sh           --epic {EPIC} --folder in-progress --depth 4

Refer to {TARGET_REPO}/project/tasks/README.md for task system documentation.\
"""
        valid_outcomes = "HANDLER_SUBTASKS_READY | HANDLER_NEED_HELP"
        job_section = ""

    elif role == "LEAF_COMPLETE_HANDLER" and ROLE_PROMPTS.get(role) is None:
        current_job_path = CURRENT_JOB_FILE.read_text().strip() if CURRENT_JOB_FILE.exists() else "<job doc path>"
        role_instructions = f"""\
You are the LEAF COMPLETE HANDLER for the ai-builder pipeline.

Target repository : {TARGET_REPO}
Epic              : {EPIC}
Current job doc   : {current_job_path}

The TESTER has just completed a subtask (TESTER_TESTS_PASS).
The current job doc is the completed subtask's README.

Your job:
1. Run on-task-complete.sh with the current job doc path:
     RESULT=$({PM_SCRIPTS_DIR}/on-task-complete.sh --current <current-job-doc> --output-dir {output_dir} --epic {EPIC})

2. Interpret the result:
   - "NEXT <path>"  → more subtasks remain; output OUTCOME: HANDLER_SUBTASKS_READY
   - "DONE"         → all subtasks complete; output OUTCOME: HANDLER_ALL_DONE
   - "STOP_AFTER"   → human review required; output OUTCOME: HANDLER_STOP_AFTER
                      Include in HANDOFF: which subtask completed, what was
                      implemented, TESTER results, and that Oracle intervention
                      is required before continuing.

Available tools:
  {PM_SCRIPTS_DIR}/on-task-complete.sh --current <readme-path> --output-dir {output_dir} --epic {EPIC}

Refer to {TARGET_REPO}/project/tasks/README.md for task system documentation.\
"""
        valid_outcomes = "HANDLER_SUBTASKS_READY | HANDLER_ALL_DONE | HANDLER_STOP_AFTER | HANDLER_NEED_HELP"
        job_section = ""

    else:
        role_file = ROLE_PROMPTS.get(role) or (ROLES_DIR / f"{role}.md")
        role_instructions = role_file.read_text() if role_file.exists() \
            else "Complete the work described in the job document."
        if role == "ARCHITECT":
            job_content = job_doc.read_text() if job_doc and job_doc.exists() else ""
            complexity_match = re.search(r'\|\s*Complexity\s*\|\s*(\S+)\s*\|', job_content)
            complexity = complexity_match.group(1) if complexity_match else "—"
            if complexity == "atomic":
                # Atomic component subtask: design mode
                valid_outcomes = "ARCHITECT_DESIGN_READY | ARCHITECT_NEEDS_REVISION | ARCHITECT_NEED_HELP"
            elif complexity in ("composite", "—"):
                # composite = needs further decomposition; — = top-level service (unset)
                valid_outcomes = "ARCHITECT_DECOMPOSITION_READY | ARCHITECT_NEEDS_REVISION | ARCHITECT_NEED_HELP"
            else:
                # Fallback for legacy job docs without a Complexity field
                valid_outcomes = "ARCHITECT_DESIGN_READY | ARCHITECT_DECOMPOSITION_READY | ARCHITECT_NEED_HELP"
        elif role == "IMPLEMENTOR":
            valid_outcomes = "IMPLEMENTOR_IMPLEMENTATION_DONE | IMPLEMENTOR_NEEDS_ARCHITECT | IMPLEMENTOR_NEED_HELP"
        elif role == "TESTER":
            valid_outcomes = "TESTER_TESTS_PASS | TESTER_TESTS_FAIL | TESTER_NEED_HELP"
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
# Execution log helpers
# ---------------------------------------------------------------------------

def log_run(role: str, agent: str, outcome: str, handoff: str) -> None:
    with EXECUTION_LOG.open("a") as f:
        f.write(f"\n{'=' * 60}\n")
        f.write(f"[{datetime.now().isoformat()}] {role}/{agent}\n")
        f.write(f"OUTCOME: {outcome}\n")
        f.write(f"HANDOFF: {handoff}\n")


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

MAX_ROLE_ITERATIONS = 3

current_role = _start_state
job_doc      = initial_job_doc
handoff_history: list[str] = []
role_iteration_counts: dict[str, int] = {}

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

    prompt = build_prompt(current_role, job_doc, OUTPUT_DIR, handoff_history)
    result: AgentResult = run_agent(agent, TIMEOUT_MINUTES, current_role, prompt, OUTPUT_DIR)

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

    if outcome.endswith("_NEED_HELP"):
        print(f"\n[orchestrator] {current_role} needs human help. Halting.")
        if job_doc:
            print(f"    Review the job document: {job_doc}")
        sys.exit(0)

    if outcome not in [o for (_, o) in ROUTES]:
        print(f"\n[orchestrator] Unrecognised outcome '{outcome}' from {current_role}. Halting.")
        sys.exit(1)

    # After a handler signals HANDLER_SUBTASKS_READY, read the current job path for downstream agents
    if current_role in ("DECOMPOSE_HANDLER", "LEAF_COMPLETE_HANDLER") and outcome == "HANDLER_SUBTASKS_READY":
        if not CURRENT_JOB_FILE.exists():
            print(f"\n[orchestrator] Handler did not write job path to {CURRENT_JOB_FILE}. Halting.")
            sys.exit(1)
        job_doc = Path(CURRENT_JOB_FILE.read_text().strip())
        if not job_doc.exists():
            print(f"\n[orchestrator] Job document not found: {job_doc}. Halting.")
            sys.exit(1)
        print(f"    current job:   {job_doc}")

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

print("\n=== Orchestrator: pipeline complete ===")
