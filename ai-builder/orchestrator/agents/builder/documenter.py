import json
import re
from pathlib import Path

from agent_wrapper import AgentResult


class DocumenterAgent:
    """Internal agent: scans output_dir for *.md files and rebuilds the
    Documentation section in README.md."""

    def run(self, job_doc: Path, output_dir: Path, **kwargs) -> AgentResult:
        task_json_path = job_doc.parent / "task.json"
        documents_written = False
        if task_json_path.exists():
            try:
                documents_written = json.loads(task_json_path.read_text()).get("documents_written", False)
            except Exception:
                pass

        if not documents_written:
            return AgentResult(exit_code=0, response="OUTCOME: DOCUMENTER_DONE\nHANDOFF: documents_written=false; skipped")

        design_docs: list[tuple[str, str]] = []
        impl_docs:   list[tuple[str, str]] = []

        for md_file in sorted(output_dir.glob("*.md")):
            if md_file.name == "README.md":
                continue
            content = md_file.read_text()

            purpose = ""
            m = re.search(r'[Pp]urpose[:\s]+([^\n.]+\.?)', content)
            if m:
                purpose = m.group(1).strip().rstrip('.')

            tags: list[str] = []
            m = re.search(r'[Tt]ags[:\s]+([^\n]+)', content)
            if m:
                tags = [t.strip() for t in m.group(1).split(',')]

            entry = (md_file.name, purpose)
            if "implementation" in tags:
                impl_docs.append(entry)
            else:
                design_docs.append(entry)

        if not design_docs and not impl_docs:
            return AgentResult(exit_code=0, response="OUTCOME: DOCUMENTER_DONE\nHANDOFF: no .md files found to index")

        lines: list[str] = ["## Documentation", ""]
        if design_docs:
            lines += ["### Design", "| File | Description |", "|------|-------------|"]
            for name, desc in design_docs:
                lines.append(f"| {name} | {desc} |")
            lines.append("")
        if impl_docs:
            lines += ["### Implementation Notes", "| File | Description |", "|------|-------------|"]
            for name, desc in impl_docs:
                lines.append(f"| {name} | {desc} |")
            lines.append("")

        doc_section = "\n".join(lines)

        readme_path = output_dir / "README.md"
        if readme_path.exists():
            readme = readme_path.read_text()
            if "## Documentation" in readme:
                readme = re.sub(r'## Documentation.*?(?=\n## |\Z)', doc_section + "\n", readme, flags=re.DOTALL)
            else:
                readme = readme.rstrip() + "\n\n" + doc_section + "\n"
        else:
            readme = f"# Documentation\n\n{doc_section}\n"
        readme_path.write_text(readme)

        n = len(design_docs) + len(impl_docs)
        return AgentResult(
            exit_code=0,
            response=(
                f"OUTCOME: DOCUMENTER_DONE\n"
                f"HANDOFF: indexed {n} doc(s) into README.md "
                f"({len(design_docs)} design, {len(impl_docs)} implementation)"
            ),
        )
