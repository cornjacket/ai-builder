import json
import re
from pathlib import Path

from agent_wrapper import AgentResult


_PLACEHOLDER_PATTERNS = [
    re.compile(r"_To be written\._", re.IGNORECASE),
    re.compile(r"\bTODO\b"),
    re.compile(r"\bFIXME\b"),
    re.compile(r"\bPLACEHOLDER\b", re.IGNORECASE),
]

def _find_empty_sections(text: str) -> list[str]:
    """Return headings whose sections are truly empty.

    A section is empty when the next non-blank line after the heading is a heading
    at the SAME or HIGHER level (same or fewer #s), or when the heading has nothing
    after it (end of file). A heading whose immediate content is only sub-headings
    (deeper # level) is NOT considered empty — those sub-headings are its content.
    """
    lines = text.splitlines()
    empties = []
    i = 0
    while i < len(lines):
        m = re.match(r'^(#{1,6})\s+(.+)', lines[i])
        if m:
            level = len(m.group(1))
            heading = lines[i].strip()
            j = i + 1
            while j < len(lines) and lines[j].strip() == '':
                j += 1
            if j >= len(lines):
                empties.append(heading)  # heading at EOF with no content
            else:
                next_m = re.match(r'^(#{1,6})\s+', lines[j])
                if next_m and len(next_m.group(1)) <= level:
                    # next non-blank is a peer or parent heading → section is empty
                    empties.append(heading)
                # else: has prose or a deeper sub-heading → not empty
        i += 1
    return empties


def _check_file(path: Path) -> list[str]:
    """Return a list of error strings for a single .md file. Empty = pass."""
    errors = []
    try:
        text = path.read_text()
    except Exception as e:
        return [f"{path.name}: cannot read file: {e}"]

    # Purpose header present
    if "Purpose:" not in text:
        errors.append(f"{path.name}: missing 'Purpose:' header")

    # Tags header present
    if "Tags:" not in text:
        errors.append(f"{path.name}: missing 'Tags:' header")

    # No empty sections
    for heading in _find_empty_sections(text):
        errors.append(f"{path.name}: empty section '{heading}'")

    # No placeholder text
    for pattern in _PLACEHOLDER_PATTERNS:
        if pattern.search(text):
            errors.append(f"{path.name}: contains placeholder text matching '{pattern.pattern}'")
            break

    return errors


class MarkdownLinterAgent:
    """Internal agent: lints .md files written in the current step.

    Reads component_type from task.json to emit typed outcomes:
      atomic step:    POST_DOC_HANDLER_ATOMIC_PASS / POST_DOC_HANDLER_ATOMIC_FAIL
      integrate step: POST_DOC_HANDLER_INTEGRATE_PASS / POST_DOC_HANDLER_INTEGRATE_FAIL
    """

    def run(self, job_doc: Path, output_dir: Path, **kwargs) -> AgentResult:
        # Determine step type from task.json
        component_type = "atomic"
        task_json = job_doc.parent / "task.json" if job_doc else None
        if task_json and task_json.exists():
            try:
                data = json.loads(task_json.read_text())
                if data.get("component_type") == "integrate":
                    component_type = "integrate"
            except Exception:
                pass

        pass_outcome = f"POST_DOC_HANDLER_{component_type.upper()}_PASS"
        fail_outcome = f"POST_DOC_HANDLER_{component_type.upper()}_FAIL"

        # Collect all .md files written to output_dir this step
        md_files = sorted(output_dir.glob("*.md"))
        if not md_files:
            return AgentResult(
                exit_code=0,
                response=f"OUTCOME: {pass_outcome}\nHANDOFF: no .md files found in {output_dir} — nothing to lint",
            )

        all_errors: list[str] = []
        for md_file in md_files:
            all_errors.extend(_check_file(md_file))

        if not all_errors:
            return AgentResult(
                exit_code=0,
                response=(
                    f"OUTCOME: {pass_outcome}\n"
                    f"HANDOFF: linted {len(md_files)} file(s) — all passed"
                ),
            )

        error_report = "\n".join(f"  - {e}" for e in all_errors)
        return AgentResult(
            exit_code=0,
            response=(
                f"OUTCOME: {fail_outcome}\n"
                f"HANDOFF: linter found {len(all_errors)} issue(s) in {len(md_files)} file(s):\n"
                f"{error_report}\n"
                f"Fix the issues listed above and resubmit."
            ),
        )
