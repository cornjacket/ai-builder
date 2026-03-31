# Task: extract-tester-and-documenter-agents

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 356c4e-extract-internal-agents-into-configurable-modules             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Move `_run_tester_internal` into `agents/tester.py` as `TesterAgent` and
`_run_documenter_internal` into `agents/documenter.py` as `DocumenterAgent`.
Both are self-contained with no orchestrator-level globals — the easiest
extractions.

## Context

These two functions reference only their explicit parameters and standard
library. No `AgentContext` injection is needed.

**`agents/tester.py`** — wraps `_run_tester_internal` (~28 lines):
- Reads `task.json` from `job_doc.parent`
- Extracts `test_command` field
- Runs it via `subprocess.run(shell=True)`
- Returns `AgentResult` with `TESTER_TESTS_PASS` or `TESTER_TESTS_FAIL`

**`agents/documenter.py`** — wraps `_run_documenter_internal` (~78 lines):
- Checks `documents_written` flag in `task.json`
- Scans `output_dir` for `.md` files
- Extracts `Purpose:`/`Tags:` metadata
- Rebuilds the Documentation section in `README.md`
- Returns `AgentResult` with `DOCUMENTER_DONE`

Both classes must satisfy the `InternalAgent` Protocol from `agents/base.py`.
After extraction, the private functions in `orchestrator.py` are deleted and
replaced with imports.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Unit Tests

Add `tests/unit/test_agents.py` (new file) with the following test cases.

**TesterAgent**

```python
class TestTesterAgent(unittest.TestCase):
    def test_passing_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            task_json = Path(tmp) / "task.json"
            task_json.write_text(json.dumps({"test_command": "true"}))
            agent = TesterAgent()
            result = agent.run(job_doc=task_json, output_dir=Path(tmp))
            self.assertEqual(result.exit_code, 0)
            self.assertIn("TESTER_TESTS_PASS", result.response)

    def test_failing_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            task_json = Path(tmp) / "task.json"
            task_json.write_text(json.dumps({"test_command": "false"}))
            agent = TesterAgent()
            result = agent.run(job_doc=task_json, output_dir=Path(tmp))
            self.assertIn("TESTER_TESTS_FAIL", result.response)

    def test_satisfies_internal_agent_protocol(self):
        self.assertIsInstance(TesterAgent(), InternalAgent)
```

**DocumenterAgent**

```python
class TestDocumenterAgent(unittest.TestCase):
    def test_rebuilds_documentation_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            # Write a .md file with Purpose/Tags metadata
            (out / "service.md").write_text(
                "# service\nPurpose: handles requests\nTags: api, core\n"
            )
            # Write a minimal README with a Documentation section placeholder
            readme = out / "README.md"
            readme.write_text("# Task\n\n## Documentation\n\n_None._\n")
            task_json = out / "task.json"
            task_json.write_text(json.dumps({"documents_written": False}))
            agent = DocumenterAgent()
            result = agent.run(job_doc=task_json, output_dir=out)
            self.assertEqual(result.exit_code, 0)
            self.assertIn("DOCUMENTER_DONE", result.response)
            content = readme.read_text()
            self.assertIn("service.md", content)

    def test_satisfies_internal_agent_protocol(self):
        self.assertIsInstance(DocumenterAgent(), InternalAgent)
```
