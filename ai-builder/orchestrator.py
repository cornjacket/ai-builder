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

REPO_ROOT       = Path(__file__).resolve().parent.parent
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
    initial_job_doc = None
else:
    initial_job_doc = args.job.resolve()


# ---------------------------------------------------------------------------
# Pipeline config
# ---------------------------------------------------------------------------

AGENTS = {
    "TASK_MANAGER": "claude",
    "ARCHITECT":       "claude",
    "IMPLEMENTOR":     "gemini",
    "TESTER":          "claude",
}

ROUTES = {
    ("ARCHITECT",   "DONE"):            "IMPLEMENTOR",
    ("ARCHITECT",   "NEED_HELP"):       None,
    ("IMPLEMENTOR", "DONE"):            "TESTER",
    ("IMPLEMENTOR", "NEEDS_ARCHITECT"): "ARCHITECT",
    ("IMPLEMENTOR", "NEED_HELP"):       None,
    ("TESTER",      "FAILED"):          "IMPLEMENTOR",
    ("TESTER",      "NEED_HELP"):       None,
}

if TM_MODE:
    ROUTES.update({
        ("TASK_MANAGER", "JOBS_READY"): "ARCHITECT",
        ("TASK_MANAGER", "ALL_DONE"):   None,
        ("TASK_MANAGER", "NEED_HELP"):  None,
        ("TESTER",          "DONE"):       "TASK_MANAGER",
    })
else:
    ROUTES[("TESTER", "DONE")] = None  # halt on completion in non-TM mode


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def build_prompt(role: str, job_doc: Path | None, output_dir: Path, handoff_history: list[str]) -> str:
    history_section = ""
    if handoff_history:
        history_section = "\n\n## Handoff Notes from Previous Agents\n\n" + \
            "\n\n---\n\n".join(handoff_history)

    if role == "TASK_MANAGER":
        is_first_run = not CURRENT_JOB_FILE.exists()
        if is_first_run:
            request_text = REQUEST or "(no request file provided)"
            role_instructions = f"""\
You are the TASK MANAGER for the ai-builder pipeline.

Target repository : {TARGET_REPO}
Epic              : {EPIC}
Job state file    : {CURRENT_JOB_FILE}

Project request:
{request_text}

Your job:
1. If the task system is not yet installed in the target repo, run:
     {SETUP_SCRIPT} {TARGET_REPO} --epic {EPIC}
     {INIT_SCRIPT} {TARGET_REPO}
2. Decompose the project request into tasks. For each task:
     {PM_SCRIPTS_DIR}/new-task.sh --epic {EPIC} --folder draft --name <task-name>
3. Refine and order tasks, moving them to backlog/ by priority:
     {PM_SCRIPTS_DIR}/move-task.sh --epic {EPIC} --name <id-task-name> --from draft --to backlog
4. Move the first task to in-progress/:
     {PM_SCRIPTS_DIR}/move-task.sh --epic {EPIC} --name <id-task-name> --from backlog --to in-progress
5. Create a job document for the first task using the template at:
     {REPO_ROOT}/ai-builder/JOB-TEMPLATE.md
   Write the job document to: {output_dir}/<task-name>.md
   Populate the Goal section from the task README Description.
6. Write the absolute path to the job document to: {CURRENT_JOB_FILE}

Refer to {TARGET_REPO}/project/tasks/README.md for task system documentation.\
"""
        else:
            role_instructions = f"""\
You are the TASK MANAGER for the ai-builder pipeline.

Target repository : {TARGET_REPO}
Epic              : {EPIC}
Job state file    : {CURRENT_JOB_FILE}

The pipeline just completed a job. Review the handoff notes below.

Your job:
1. Mark the completed task done:
     {PM_SCRIPTS_DIR}/complete-task.sh --epic {EPIC} --folder in-progress --name <id-task-name>
2. Check for remaining work:
     {PM_SCRIPTS_DIR}/list-tasks.sh --epic {EPIC} --folder backlog --depth 1
3. If tasks remain:
   - Move the next task to in-progress/
   - Create a job document for it using {REPO_ROOT}/ai-builder/JOB-TEMPLATE.md
     Write it to: {output_dir}/<task-name>.md
   - Write its absolute path to: {CURRENT_JOB_FILE}
   - Output OUTCOME: JOBS_READY
4. If no tasks remain: output OUTCOME: ALL_DONE\
"""
        valid_outcomes = "JOBS_READY | ALL_DONE | NEED_HELP"
        job_section = ""

    else:
        role_file = ROLES_DIR / f"{role}.md"
        role_instructions = role_file.read_text() if role_file.exists() \
            else "Complete the work described in the job document."
        valid_outcomes = {
            "ARCHITECT":   "DONE | NEED_HELP",
            "IMPLEMENTOR": "DONE | NEEDS_ARCHITECT | NEED_HELP",
            "TESTER":      "DONE | FAILED | NEED_HELP",
        }.get(role, "DONE | NEED_HELP")
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

current_role = "TASK_MANAGER" if TM_MODE else "ARCHITECT"
job_doc      = initial_job_doc
handoff_history: list[str] = []

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

    if outcome == "NEED_HELP":
        print(f"\n[orchestrator] {current_role} needs human help. Halting.")
        if job_doc:
            print(f"    Review the job document: {job_doc}")
        sys.exit(0)

    if outcome not in [o for (_, o) in ROUTES]:
        print(f"\n[orchestrator] Unrecognised outcome '{outcome}' from {current_role}. Halting.")
        sys.exit(1)

    # After TM signals JOBS_READY, read the current job path for downstream agents
    if current_role == "TASK_MANAGER" and outcome == "JOBS_READY":
        if not CURRENT_JOB_FILE.exists():
            print(f"\n[orchestrator] TM did not write job path to {CURRENT_JOB_FILE}. Halting.")
            sys.exit(1)
        job_doc = Path(CURRENT_JOB_FILE.read_text().strip())
        if not job_doc.exists():
            print(f"\n[orchestrator] Job document not found: {job_doc}. Halting.")
            sys.exit(1)
        print(f"    current job:   {job_doc}")

    current_role = ROUTES.get((current_role, outcome))

print("\n=== Orchestrator: pipeline complete ===")
