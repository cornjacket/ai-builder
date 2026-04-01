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
from agents.doc.linter import MarkdownLinterAgent


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


class TestLCHAgentRouteOn(unittest.TestCase):
    def _make_task_json(self, tmp: str, component_type: str | None = None) -> Path:
        data: dict = {}
        if component_type is not None:
            data["component_type"] = component_type
        p = Path(tmp) / "task.json"
        p.write_text(json.dumps(data))
        return p

    def _agent(self, route_on: dict | None) -> LCHAgent:
        return LCHAgent(ctx=_minimal_ctx(), route_on=route_on)

    def test_no_route_on_returns_subtasks_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            next_readme = self._make_task_json(tmp)
            outcome = self._agent(None)._resolve_next_outcome(str(next_readme))
            self.assertEqual(outcome, "HANDLER_SUBTASKS_READY")

    def test_default_when_field_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            next_readme = self._make_task_json(tmp)  # no component_type
            route_on = {"field": "component_type", "default": "HANDLER_SUBTASKS_READY", "integrate": "HANDLER_INTEGRATE_READY"}
            outcome = self._agent(route_on)._resolve_next_outcome(str(next_readme))
            self.assertEqual(outcome, "HANDLER_SUBTASKS_READY")

    def test_matched_value_returns_mapped_outcome(self):
        with tempfile.TemporaryDirectory() as tmp:
            next_readme = self._make_task_json(tmp, component_type="integrate")
            route_on = {"field": "component_type", "default": "HANDLER_SUBTASKS_READY", "integrate": "HANDLER_INTEGRATE_READY"}
            outcome = self._agent(route_on)._resolve_next_outcome(str(next_readme))
            self.assertEqual(outcome, "HANDLER_INTEGRATE_READY")

    def test_missing_default_key_falls_back_gracefully(self):
        with tempfile.TemporaryDirectory() as tmp:
            next_readme = self._make_task_json(tmp, component_type="integrate")
            route_on = {"field": "component_type", "integrate": "HANDLER_INTEGRATE_READY"}  # no default
            outcome = self._agent(route_on)._resolve_next_outcome(str(next_readme))
            self.assertEqual(outcome, "HANDLER_SUBTASKS_READY")

    def test_missing_task_json_returns_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            route_on = {"field": "component_type", "default": "HANDLER_SUBTASKS_READY", "integrate": "HANDLER_INTEGRATE_READY"}
            outcome = self._agent(route_on)._resolve_next_outcome(str(Path(tmp) / "nonexistent" / "README.md"))
            self.assertEqual(outcome, "HANDLER_SUBTASKS_READY")


class TestMarkdownLinterAgent(unittest.TestCase):
    _VALID_MD = "# store.go\n\nPurpose: Manages user records.\n\nTags: data-access\n\n## Public API\n\nsome content\n"

    def _run(self, files: dict[str, str], component_type: str | None = None) -> "AgentResult":  # type: ignore[name-defined]
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            for name, content in files.items():
                (tmp_path / name).write_text(content)
            task_json = tmp_path / "task.json"
            data: dict = {}
            if component_type:
                data["component_type"] = component_type
            task_json.write_text(json.dumps(data))
            job_doc = task_json
            return MarkdownLinterAgent().run(job_doc=job_doc, output_dir=tmp_path)

    def test_pass_atomic(self):
        result = self._run({"store.md": self._VALID_MD})
        self.assertIn("POST_DOC_HANDLER_ATOMIC_PASS", result.response)

    def test_pass_integrate(self):
        result = self._run({"README.md": self._VALID_MD}, component_type="integrate")
        self.assertIn("POST_DOC_HANDLER_INTEGRATE_PASS", result.response)

    def test_fail_missing_purpose(self):
        result = self._run({"store.md": "# store.go\n\nTags: data-access\n\ncontent\n"})
        self.assertIn("POST_DOC_HANDLER_ATOMIC_FAIL", result.response)
        self.assertIn("Purpose", result.response)

    def test_fail_missing_tags(self):
        result = self._run({"store.md": "# store.go\n\nPurpose: Does things.\n\ncontent\n"})
        self.assertIn("POST_DOC_HANDLER_ATOMIC_FAIL", result.response)
        self.assertIn("Tags", result.response)

    def test_fail_placeholder_text(self):
        result = self._run({"store.md": "# store.go\n\nPurpose: x\n\nTags: x\n\n_To be written._\n"})
        self.assertIn("POST_DOC_HANDLER_ATOMIC_FAIL", result.response)
        self.assertIn("placeholder", result.response)

    def test_fail_empty_section(self):
        md = "# store.go\n\nPurpose: x\n\nTags: x\n\n## Public API\n\n## Dependencies\n\ncontent\n"
        result = self._run({"store.md": md})
        self.assertIn("POST_DOC_HANDLER_ATOMIC_FAIL", result.response)
        self.assertIn("empty section", result.response)

    def test_no_md_files_passes(self):
        result = self._run({})
        self.assertIn("POST_DOC_HANDLER_ATOMIC_PASS", result.response)

    def test_fail_integrate_routes_to_integrator(self):
        result = self._run({"README.md": "# dir\n\nTags: overview\n\ncontent\n"}, component_type="integrate")
        self.assertIn("POST_DOC_HANDLER_INTEGRATE_FAIL", result.response)

    def test_satisfies_internal_agent_protocol(self):
        self.assertIsInstance(MarkdownLinterAgent(), InternalAgent)


_DOC_MACHINE_PATH = Path(__file__).resolve().parents[2] / "ai-builder" / "orchestrator" / "machines" / "doc" / "default.json"


class TestDocMachineImplPaths(unittest.TestCase):
    def test_all_impl_paths_resolve(self):
        machine = _json.loads(_DOC_MACHINE_PATH.read_text())
        ctx = _minimal_ctx()
        for role, cfg in machine["roles"].items():
            if cfg.get("agent") != "internal" or "impl" not in cfg:
                continue
            with self.subTest(role=role):
                agent = load_internal_agent(cfg["impl"], ctx)
                self.assertIsNotNone(agent)

    def test_all_resolved_agents_satisfy_protocol(self):
        machine = _json.loads(_DOC_MACHINE_PATH.read_text())
        ctx = _minimal_ctx()
        for role, cfg in machine["roles"].items():
            if cfg.get("agent") != "internal" or "impl" not in cfg:
                continue
            with self.subTest(role=role):
                agent = load_internal_agent(cfg["impl"], ctx)
                self.assertIsInstance(agent, InternalAgent)


if __name__ == "__main__":
    unittest.main()
