"""Unit tests for _parse_components_table from orchestrator.py.

The function is reproduced here (pure Python, no imports beyond re) to avoid
importing the orchestrator, which has top-level side effects (argparse).
"""

import re
import unittest


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
                "description": "|".join(parts[2:]).strip(),
            })
    return rows


# ---------------------------------------------------------------------------
# Basic parsing
# ---------------------------------------------------------------------------

class TestParseComponentsTable(unittest.TestCase):

    def _readme(self, table_rows: str) -> str:
        return (
            "## Goal\n\nBuild a service.\n\n"
            "## Components\n\n"
            "| Name | Complexity | Description |\n"
            "|------|------------|-------------|\n"
            f"{table_rows}\n"
            "## Design\n\n_To be completed._\n"
        )

    def test_empty_table(self):
        readme = self._readme("")
        result = _parse_components_table(readme)
        self.assertEqual(result, [])

    def test_single_atomic_row(self):
        readme = self._readme("| user-store | atomic | Handles user storage |")
        result = _parse_components_table(readme)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "user-store")
        self.assertEqual(result[0]["complexity"], "atomic")
        self.assertEqual(result[0]["description"], "Handles user storage")

    def test_two_rows(self):
        rows = (
            "| user-store | atomic | Handles user storage |\n"
            "| integrate  | atomic | Wire components      |"
        )
        result = _parse_components_table(self._readme(rows))
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "user-store")
        self.assertEqual(result[1]["name"], "integrate")

    def test_composite_complexity(self):
        rows = "| iam | composite | IAM subsystem with auth and authz |"
        result = _parse_components_table(self._readme(rows))
        self.assertEqual(result[0]["complexity"], "composite")

    def test_row_order_preserved(self):
        rows = (
            "| a | atomic | First  |\n"
            "| b | atomic | Second |\n"
            "| c | atomic | Third  |"
        )
        result = _parse_components_table(self._readme(rows))
        self.assertEqual([r["name"] for r in result], ["a", "b", "c"])

    def test_no_components_section(self):
        readme = "## Goal\n\nBuild something.\n\n## Design\n\nNo components.\n"
        result = _parse_components_table(readme)
        self.assertEqual(result, [])

    def test_description_with_pipe_characters(self):
        """Descriptions may contain | (e.g., API contract notation)."""
        rows = "| handler | atomic | POST /users → 201 | GET /users/{id} → 200 |"
        result = _parse_components_table(self._readme(rows))
        self.assertEqual(len(result), 1)
        self.assertIn("POST /users", result[0]["description"])

    def test_stops_at_next_section(self):
        readme = (
            "## Components\n\n"
            "| Name | Complexity | Description |\n"
            "|------|------------|-------------|\n"
            "| auth | atomic | Auth component |\n"
            "\n"
            "## Design\n\n"
            "| Name | Complexity | Description |\n"  # should not be parsed
            "|------|------------|-------------|\n"
            "| fake | atomic | Should not appear |\n"
        )
        result = _parse_components_table(readme)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "auth")


# ---------------------------------------------------------------------------
# Realistic ARCHITECT output
# ---------------------------------------------------------------------------

class TestRealisticOutput(unittest.TestCase):

    SAMPLE_README = """\
# Task: build-1

## Goal

Build a user management HTTP service.

## Context

Regression test for the pipeline.

## Components

A simple service with two components: store and handler.

| Name | Complexity | Description |
|------|------------|-------------|
| user-store | atomic | In-memory store for user records. Fields: id (string), username (string), password (string). Methods: Create, Get, Update, Delete. |
| user-handler | atomic | HTTP handler. POST /users {"username":string,"password":string} → 201 {"id":string,"username":string}; GET /users/{id} → 200 or 404; PUT /users/{id} body → 200 or 404; DELETE /users/{id} → 204 or 404 |
| integrate | atomic | Wire user-store and user-handler into a running HTTP service on port 8080. Verify all endpoints pass acceptance criteria. |

## Design

_To be completed by the ARCHITECT._
"""

    def test_parses_three_components(self):
        result = _parse_components_table(self.SAMPLE_README)
        self.assertEqual(len(result), 3)

    def test_last_is_integrate(self):
        result = _parse_components_table(self.SAMPLE_README)
        self.assertEqual(result[-1]["name"], "integrate")

    def test_all_atomic(self):
        result = _parse_components_table(self.SAMPLE_README)
        for row in result:
            self.assertEqual(row["complexity"], "atomic")

    def test_descriptions_nonempty(self):
        result = _parse_components_table(self.SAMPLE_README)
        for row in result:
            self.assertGreater(len(row["description"]), 0)


if __name__ == "__main__":
    unittest.main()
