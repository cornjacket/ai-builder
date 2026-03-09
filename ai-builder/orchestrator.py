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
    "--task",
    type=Path,
    required=True,
    help="Path to the task document (e.g. tests/regression/fibonacci/TASK-fibonacci-demo.md)",
)
parser.add_argument(
    "--output-dir",
    type=Path,
    required=True,
    help="Directory where generated artifacts and logs are written",
)
args = parser.parse_args()

TASK_DOC    = args.task.resolve()
OUTPUT_DIR  = args.output_dir.resolve()
TIMEOUT_MINUTES = 5

if not TASK_DOC.exists():
    print(f"[orchestrator] Task document not found: {TASK_DOC}")
    sys.exit(1)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
EXECUTION_LOG = OUTPUT_DIR / "execution.log"

# ---------------------------------------------------------------------------
# Pipeline config
# ---------------------------------------------------------------------------

# Fixed pipeline: role -> agent CLI
AGENTS = {
    "ARCHITECT":   "claude",
    "IMPLEMENTOR": "gemini",
    "TESTER":      "claude",
}

# Routing table: (current_role, outcome) -> next_role or None (halt)
ROUTES = {
    ("ARCHITECT",   "DONE"):             "IMPLEMENTOR",
    ("ARCHITECT",   "NEED_HELP"):        None,
    ("IMPLEMENTOR", "DONE"):             "TESTER",
    ("IMPLEMENTOR", "NEEDS_ARCHITECT"):  "ARCHITECT",
    ("IMPLEMENTOR", "NEED_HELP"):        None,
    ("TESTER",      "DONE"):             None,   # pipeline complete
    ("TESTER",      "FAILED"):           "IMPLEMENTOR",
    ("TESTER",      "NEED_HELP"):        None,
}


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def build_prompt(role: str, task_doc: Path, output_dir: Path, handoff_history: list[str]) -> str:
    history_section = ""
    if handoff_history:
        history_section = "\n\n## Handoff Notes from Previous Agents\n\n" + \
            "\n\n---\n\n".join(handoff_history)

    role_instructions = {
        "ARCHITECT": (
            "Read the Goal section. Fill in the Design and Acceptance Criteria "
            "sections of the task document by editing it directly. Be concrete and specific. "
            "Break the work into well-scoped steps so that each implementation step is small "
            "enough that the IMPLEMENTOR requires minimal internal testing."
        ),
        "IMPLEMENTOR": (
            "Read the Design section of the task document. Implement exactly what is "
            "specified. Write output files to the output directory stated below.\n\n"
            "Testing boundaries:\n"
            "- Always run a syntax/compile check after writing the file.\n"
            "- Do not introduce functions, classes, or modules not specified in the Design. "
            "If the Design explicitly calls for a module with internal functions, you may "
            "run minimal happy-path tests of those internals only. Otherwise, a syntax "
            "check is sufficient.\n"
            "- Do NOT run acceptance tests. Do NOT test the public interface or CLI behaviour — "
            "that is the TESTER's exclusive responsibility."
        ),
        "TESTER": (
            "Read the Design and Acceptance Criteria sections of the task document. "
            "Run the program and verify every expected output. Report pass/fail for each case."
        ),
    }

    return f"""Your role is {role}.

The shared task document is at: {task_doc}

Output directory (write all generated files here): {output_dir}

{role_instructions.get(role, "Complete the work described in the task document.")}
{history_section}

When you are finished, end your response with exactly this block (fill in the values):

OUTCOME: DONE | NEEDS_ARCHITECT | FAILED | NEED_HELP | RATE_LIMIT_PAUSE
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

print("=== Orchestrator: starting ===")
print(f"    task doc:      {TASK_DOC}")
print(f"    output dir:    {OUTPUT_DIR}")
print(f"    execution log: {EXECUTION_LOG}\n")

current_role = "ARCHITECT"
handoff_history: list[str] = []

while current_role is not None:
    agent = AGENTS.get(current_role)
    if agent is None:
        print(f"[orchestrator] No agent configured for role {current_role}. Halting.")
        sys.exit(1)

    print(f"\n>>> [{current_role} / {agent}]")

    prompt = build_prompt(current_role, TASK_DOC, OUTPUT_DIR, handoff_history)
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

    next_role = ROUTES.get((current_role, outcome))

    if outcome == "NEED_HELP":
        print(f"\n[orchestrator] {current_role} needs human help. Halting.")
        print(f"    Review the task document: {TASK_DOC}")
        sys.exit(0)

    if outcome not in [o for (_, o) in ROUTES]:
        print(f"\n[orchestrator] Unrecognised outcome '{outcome}' from {current_role}. Halting.")
        sys.exit(1)

    current_role = next_role

print("\n=== Orchestrator: pipeline complete ===")
