import argparse
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
    "--request",
    type=Path,
    help="Path to project request file (TM mode only)",
)
args = parser.parse_args()

TM_MODE = args.target_repo is not None

if TM_MODE:
    if not args.target_repo.exists():
        print(f"[orchestrator] Target repo not found: {args.target_repo}")
        sys.exit(1)
    if args.request and not args.request.exists():
        print(f"[orchestrator] Request file not found: {args.request}")
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
OUTPUT_DIR      = args.output_dir.resolve()
TIMEOUT_MINUTES = 5

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
EXECUTION_LOG    = OUTPUT_DIR / "execution.log"
CURRENT_JOB_FILE = OUTPUT_DIR / "current-job.txt"

if TM_MODE:
    TARGET_REPO    = args.target_repo.resolve()
    EPIC           = args.epic
    REQUEST        = args.request.read_text() if args.request else None
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
# Pipeline config
# ---------------------------------------------------------------------------

AGENTS = {
    "TASK_MANAGER": "claude",
    "ARCHITECT":    "claude",
    "IMPLEMENTOR":  "claude",
    "TESTER":       "claude",
}

ROUTES = {
    ("ARCHITECT",   "ARCHITECT_DESIGN_READY"):           "IMPLEMENTOR",
    ("ARCHITECT",   "ARCHITECT_NEED_HELP"):              None,
    ("IMPLEMENTOR", "IMPLEMENTOR_IMPLEMENTATION_DONE"):  "TESTER",
    ("IMPLEMENTOR", "IMPLEMENTOR_NEEDS_ARCHITECT"):      "ARCHITECT",
    ("IMPLEMENTOR", "IMPLEMENTOR_NEED_HELP"):            None,
    ("TESTER",      "TESTER_TESTS_FAIL"):                "IMPLEMENTOR",
    ("TESTER",      "TESTER_NEED_HELP"):                 None,
}

if TM_MODE:
    ROUTES.update({
        ("ARCHITECT",    "ARCHITECT_DECOMPOSITION_READY"): "TASK_MANAGER",
        ("ARCHITECT",    "ARCHITECT_NEEDS_REVISION"):      "ARCHITECT",
        ("TASK_MANAGER", "TM_SUBTASKS_READY"):             "ARCHITECT",
        ("TASK_MANAGER", "TM_ALL_DONE"):                   None,
        ("TASK_MANAGER", "TM_STOP_AFTER"):                 None,
        ("TASK_MANAGER", "TM_NEED_HELP"):                  None,
        ("TESTER",       "TESTER_TESTS_PASS"):             "TASK_MANAGER",
    })
else:
    ROUTES[("TESTER", "TESTER_TESTS_PASS")] = None  # halt on completion in non-TM mode


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def build_prompt(role: str, job_doc: Path | None, output_dir: Path, handoff_history: list[str], last_outcome: str = "") -> str:
    history_section = ""
    if handoff_history:
        history_section = "\n\n## Handoff Notes from Previous Agents\n\n" + \
            "\n\n---\n\n".join(handoff_history)

    if role == "TASK_MANAGER":
        current_job_path = CURRENT_JOB_FILE.read_text().strip() if CURRENT_JOB_FILE.exists() else "<job doc path>"
        if last_outcome == "ARCHITECT_DECOMPOSITION_READY":
            role_instructions = f"""\
You are the TASK MANAGER for the ai-builder pipeline.

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

8. Output OUTCOME: TM_SUBTASKS_READY

Available tools:
  {PM_SCRIPTS_DIR}/new-pipeline-subtask.sh --epic {EPIC} --folder in-progress --parent <parent-rel-path> --name <name>
  {PM_SCRIPTS_DIR}/set-current-job.sh      --output-dir {output_dir} <task-readme-path>
  {PM_SCRIPTS_DIR}/list-tasks.sh           --epic {EPIC} --folder in-progress --depth 4

Refer to {TARGET_REPO}/project/tasks/README.md for task system documentation.\
"""
        else:
            role_instructions = f"""\
You are the TASK MANAGER for the ai-builder pipeline.

Target repository : {TARGET_REPO}
Epic              : {EPIC}
Current job doc   : {current_job_path}

The TESTER has just completed a subtask (TESTER_TESTS_PASS).
The current job doc is the completed subtask's README.

Your job:
1. Run on-task-complete.sh with the current job doc path:
     RESULT=$({PM_SCRIPTS_DIR}/on-task-complete.sh --current <current-job-doc> --output-dir {output_dir} --epic {EPIC})

2. Interpret the result:
   - "NEXT <path>"  → more subtasks remain; output OUTCOME: TM_SUBTASKS_READY
   - "DONE"         → all subtasks complete; output OUTCOME: TM_ALL_DONE
   - "STOP_AFTER"   → human review required; output OUTCOME: TM_STOP_AFTER
                      Include in HANDOFF: which subtask completed, what was
                      implemented, TESTER results, and that Oracle intervention
                      is required before continuing.

Available tools:
  {PM_SCRIPTS_DIR}/on-task-complete.sh --current <readme-path> --output-dir {output_dir} --epic {EPIC}

Refer to {TARGET_REPO}/project/tasks/README.md for task system documentation.\
"""
        valid_outcomes = "TM_SUBTASKS_READY | TM_ALL_DONE | TM_STOP_AFTER | TM_NEED_HELP"
        job_section = ""

    else:
        role_file = ROLES_DIR / f"{role}.md"
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

current_role = "ARCHITECT"  # always starts at ARCHITECT; TM only runs when routed to it
job_doc      = initial_job_doc
handoff_history: list[str] = []
role_iteration_counts: dict[str, int] = {}
last_outcome: str = ""

print("=== Orchestrator: starting ===")
if TM_MODE:
    print(f"    mode:          TM")
    print(f"    target repo:   {TARGET_REPO}")
    print(f"    epic:          {EPIC}")
    print(f"    request:       {args.request or '(none)'}")
else:
    print(f"    job doc:       {job_doc}")
print(f"    output dir:    {OUTPUT_DIR}")
print(f"    execution log: {EXECUTION_LOG}\n")

while current_role is not None:
    agent = AGENTS.get(current_role)
    if agent is None:
        print(f"[orchestrator] No agent configured for role {current_role}. Halting.")
        sys.exit(1)

    print(f"\n>>> [{current_role} / {agent}]")

    prompt = build_prompt(current_role, job_doc, OUTPUT_DIR, handoff_history, last_outcome)
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
    last_outcome = outcome

    print(f"\n<<< [{current_role}] outcome={outcome}")

    if outcome.endswith("_NEED_HELP"):
        print(f"\n[orchestrator] {current_role} needs human help. Halting.")
        if job_doc:
            print(f"    Review the job document: {job_doc}")
        sys.exit(0)

    if outcome not in [o for (_, o) in ROUTES]:
        print(f"\n[orchestrator] Unrecognised outcome '{outcome}' from {current_role}. Halting.")
        sys.exit(1)

    # After TM signals TM_SUBTASKS_READY, read the current job path for downstream agents
    if current_role == "TASK_MANAGER" and outcome == "TM_SUBTASKS_READY":
        if not CURRENT_JOB_FILE.exists():
            print(f"\n[orchestrator] TM did not write job path to {CURRENT_JOB_FILE}. Halting.")
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
