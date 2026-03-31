from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AgentContext:
    """Orchestrator-level constants injected into agents that need them."""
    run_dir:          Path
    current_job_file: Path
    pm_scripts_dir:   Path
    epic:             str
    output_dir:       Path
    target_repo:      Path | None = None
