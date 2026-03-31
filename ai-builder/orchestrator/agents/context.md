# agents/context.py

Defines `AgentContext` — the dependency injection container passed to internal
agents that need orchestrator-level constants.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `run_dir` | `Path` | Directory holding `current-job.txt`, `execution.log`, etc. Defaults to `--output-dir`. |
| `current_job_file` | `Path` | Path to `current-job.txt`; read by LCHAgent to find the active task. |
| `pm_scripts_dir` | `Path` | `<target-repo>/project/tasks/scripts/`; parent of all TM shell scripts. |
| `epic` | `str` | Epic name (e.g. `"main"`); passed as `--epic` to TM scripts. |
| `output_dir` | `Path` | Top-level pipeline output directory; used as fallback for component output dirs. |
| `target_repo` | `Path \| None` | Root of the target repository; used to resolve `in-progress/` paths. `None` in non-TM mode. |

## Usage

Built once in `orchestrator.py` after the CLI is parsed, then passed to
`load_internal_agent`. Context-free agents (`TesterAgent`, `DocumenterAgent`)
ignore it; context-aware agents store it as `self.ctx`.
