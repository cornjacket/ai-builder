# machines/builder/

Builder machine configurations. Each JSON file defines a complete pipeline —
agent types, prompt paths, transition table, and per-role flags.

| File | Description |
|------|-------------|
| `default.json` | Full TM pipeline (Claude). Use when `--target-repo` is provided. |
| `simple.json` | Flat single-step pipeline (Claude). Use when only `--job` is provided. |
| `default-gemini.json` | Full TM pipeline (Gemini for ARCHITECT/IMPLEMENTOR). |
| `simple-gemini.json` | Flat single-step pipeline (Gemini for ARCHITECT/IMPLEMENTOR). |
| `roles/` | AI agent prompt files for this machine — ARCHITECT.md and IMPLEMENTOR.md |

## Choosing a machine

- **`default.json`** — standard pipeline run against a target repo with full
  task management, decomposition, and leaf completion handling
- **`simple.json`** — single-component builds with no task management; useful
  for quick experiments or pipelines that manage tasks externally
- **Gemini variants** — same topology as their Claude counterparts but route
  ARCHITECT and IMPLEMENTOR through the Gemini API; TESTER remains internal

## Passing a custom machine

```bash
python3 ai-builder/orchestrator/orchestrator.py \
    --job <job-doc> \
    --state-machine ai-builder/orchestrator/machines/builder/default.json \
    ...
```
