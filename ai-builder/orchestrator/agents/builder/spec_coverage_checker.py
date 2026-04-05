import json
import re
from pathlib import Path

from agent_wrapper import AgentResult


class SpecCoverageCheckerAgent:
    """Internal agent: verifies that generated test files cover every endpoint
    in acceptance-spec.json. Runs after IMPLEMENTOR at the TOP integrate level,
    before TESTER. No-op if acceptance-spec.json is absent or has no endpoints.
    """

    def run(self, job_doc: Path, output_dir: Path, **kwargs) -> AgentResult:
        spec_file = output_dir / "acceptance-spec.json"

        if not spec_file.exists():
            return AgentResult(
                exit_code=0,
                response=(
                    "OUTCOME: SPEC_COVERAGE_CHECKER_PASS\n"
                    "HANDOFF: No acceptance-spec.json in output_dir — skipping coverage check."
                ),
            )

        try:
            spec = json.loads(spec_file.read_text())
        except Exception as e:
            return AgentResult(
                exit_code=1,
                response=f"OUTCOME: SPEC_COVERAGE_CHECKER_FAIL\nHANDOFF: Failed to parse acceptance-spec.json: {e}",
            )

        endpoints = spec.get("endpoints", [])
        if not endpoints:
            return AgentResult(
                exit_code=0,
                response=(
                    "OUTCOME: SPEC_COVERAGE_CHECKER_PASS\n"
                    "HANDOFF: acceptance-spec.json has no endpoints — nothing to check."
                ),
            )

        # Collect all test files under output_dir.
        test_patterns = ["*_test.go", "*_test.py", "*.test.ts", "*.test.js", "*.spec.ts", "*.spec.js"]
        test_files = []
        for pattern in test_patterns:
            test_files.extend(output_dir.rglob(pattern))

        if not test_files:
            missing = [f"{e['method']} {e['path']}" for e in endpoints]
            report = "\n".join(f"  - {m}" for m in missing)
            return AgentResult(
                exit_code=0,
                response=(
                    f"OUTCOME: SPEC_COVERAGE_CHECKER_FAIL\n"
                    f"HANDOFF: No test files found under {output_dir}. "
                    f"All {len(endpoints)} endpoint(s) uncovered:\n{report}"
                ),
            )

        test_content = "\n".join(_safe_read(f) for f in test_files)

        uncovered = []
        for endpoint in endpoints:
            path_pattern = _path_to_regex(endpoint["path"])
            if not re.search(path_pattern, test_content):
                uncovered.append(f"{endpoint['method']} {endpoint['path']}")

        if uncovered:
            report = "\n".join(f"  - {u}" for u in uncovered)
            return AgentResult(
                exit_code=0,
                response=(
                    f"OUTCOME: SPEC_COVERAGE_CHECKER_FAIL\n"
                    f"HANDOFF: {len(uncovered)} endpoint(s) not found in test files:\n"
                    f"{report}\n"
                    f"Ensure tests reference these paths before TESTER runs."
                ),
            )

        return AgentResult(
            exit_code=0,
            response=(
                f"OUTCOME: SPEC_COVERAGE_CHECKER_PASS\n"
                f"HANDOFF: All {len(endpoints)} endpoint(s) covered by test files."
            ),
        )


def _path_to_regex(path: str) -> str:
    """Convert a spec path like /roles/{id} to a regex that matches /roles/123."""
    escaped = re.escape(path)
    # Replace escaped {param} placeholders with a pattern matching one path segment.
    return re.sub(r"\\\{[^}]+\\\}", r"[^/\"'\\s]+", escaped)


def _safe_read(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except Exception:
        return ""
