from typing import Protocol, runtime_checkable
from pathlib import Path

from agent_wrapper import AgentResult


@runtime_checkable
class InternalAgent(Protocol):
    def run(self, job_doc: Path, output_dir: Path, **kwargs) -> AgentResult:
        ...
