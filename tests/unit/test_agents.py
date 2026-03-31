"""Unit tests for the agents/ package."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure the orchestrator package is on the path
import json as _json

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ai-builder" / "orchestrator"))

from agents.base import InternalAgent
from agents.context import AgentContext
from agents.loader import load_internal_agent
from agents.builder.tester import TesterAgent
from agents.builder.documenter import DocumenterAgent
from agents.builder.decompose import DecomposeAgent
from agents.builder.lch import LCHAgent


def _minimal_ctx() -> AgentContext:
    return AgentContext(
        run_dir=Path("."),
        current_job_file=Path("."),
        pm_scripts_dir=Path("."),
        epic="main",
        output_dir=Path("."),
    )


class TestTesterAgent(unittest.TestCase):
    def test_passing_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            task_json = Path(tmp) / "task.json"
            task_json.write_text(json.dumps({"test_command": "true"}))
            result = TesterAgent().run(job_doc=task_json, output_dir=Path(tmp))
            self.assertEqual(result.exit_code, 0)
            self.assertIn("TESTER_TESTS_PASS", result.response)

    def test_failing_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            task_json = Path(tmp) / "task.json"
            task_json.write_text(json.dumps({"test_command": "false"}))
            result = TesterAgent().run(job_doc=task_json, output_dir=Path(tmp))
            self.assertIn("TESTER_TESTS_FAIL", result.response)

    def test_missing_task_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            task_json = Path(tmp) / "task.json"  # does not exist
            result = TesterAgent().run(job_doc=task_json, output_dir=Path(tmp))
            self.assertEqual(result.exit_code, 1)
            self.assertIn("TESTER_NEED_HELP", result.response)

    def test_missing_test_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            task_json = Path(tmp) / "task.json"
            task_json.write_text(json.dumps({}))
            result = TesterAgent().run(job_doc=task_json, output_dir=Path(tmp))
            self.assertEqual(result.exit_code, 1)
            self.assertIn("TESTER_NEED_HELP", result.response)

    def test_satisfies_internal_agent_protocol(self):
        self.assertIsInstance(TesterAgent(), InternalAgent)


class TestDocumenterAgent(unittest.TestCase):
    def test_skips_when_documents_written_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            task_json = Path(tmp) / "task.json"
            task_json.write_text(json.dumps({"documents_written": False}))
            result = DocumenterAgent().run(job_doc=task_json, output_dir=Path(tmp))
            self.assertEqual(result.exit_code, 0)
            self.assertIn("DOCUMENTER_DONE", result.response)
            self.assertIn("skipped", result.response)

    def test_rebuilds_documentation_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            task_json = out / "task.json"
            task_json.write_text(json.dumps({"documents_written": True}))
            (out / "service.md").write_text(
                "# service\nPurpose: handles HTTP requests\nTags: api, core\n"
            )
            readme = out / "README.md"
            readme.write_text("# Task\n\n## Documentation\n\n_None._\n")
            result = DocumenterAgent().run(job_doc=task_json, output_dir=out)
            self.assertEqual(result.exit_code, 0)
            self.assertIn("DOCUMENTER_DONE", result.response)
            content = readme.read_text()
            self.assertIn("service.md", content)
            self.assertIn("handles HTTP requests", content)

    def test_implementation_tag_routing(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            task_json = out / "task.json"
            task_json.write_text(json.dumps({"documents_written": True}))
            (out / "impl.md").write_text(
                "# impl\nPurpose: implements the store\nTags: implementation\n"
            )
            readme = out / "README.md"
            readme.write_text("# Task\n")
            DocumenterAgent().run(job_doc=task_json, output_dir=out)
            content = readme.read_text()
            self.assertIn("Implementation Notes", content)
            self.assertNotIn("### Design", content)

    def test_no_md_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            task_json = Path(tmp) / "task.json"
            task_json.write_text(json.dumps({"documents_written": True}))
            result = DocumenterAgent().run(job_doc=task_json, output_dir=Path(tmp))
            self.assertEqual(result.exit_code, 0)
            self.assertIn("DOCUMENTER_DONE", result.response)

    def test_satisfies_internal_agent_protocol(self):
        self.assertIsInstance(DocumenterAgent(), InternalAgent)


_MACHINE_PATH = Path(__file__).resolve().parents[2] / "ai-builder" / "orchestrator" / "machines" / "builder" / "default.json"


class TestLoadInternalAgent(unittest.TestCase):
    def test_all_impl_paths_resolve(self):
        machine = _json.loads(_MACHINE_PATH.read_text())
        ctx = _minimal_ctx()
        for role, cfg in machine["roles"].items():
            if cfg.get("agent") != "internal" or "impl" not in cfg:
                continue
            with self.subTest(role=role):
                agent = load_internal_agent(cfg["impl"], ctx)
                self.assertIsNotNone(agent)

    def test_all_resolved_agents_satisfy_protocol(self):
        machine = _json.loads(_MACHINE_PATH.read_text())
        ctx = _minimal_ctx()
        for role, cfg in machine["roles"].items():
            if cfg.get("agent") != "internal" or "impl" not in cfg:
                continue
            with self.subTest(role=role):
                agent = load_internal_agent(cfg["impl"], ctx)
                self.assertIsInstance(agent, InternalAgent)


class TestDecomposeAgentProtocol(unittest.TestCase):
    def test_satisfies_internal_agent_protocol(self):
        self.assertIsInstance(DecomposeAgent(ctx=_minimal_ctx()), InternalAgent)


class TestLCHAgentProtocol(unittest.TestCase):
    def test_satisfies_internal_agent_protocol(self):
        self.assertIsInstance(LCHAgent(ctx=_minimal_ctx()), InternalAgent)


if __name__ == "__main__":
    unittest.main()
