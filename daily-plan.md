# Daily plan — 2026-07-24

**What this repo is (for a newcomer):** `create-ai-builder` is a generator that
installs an AI-agent **build pipeline** (an orchestrator plus ARCHITECT /
IMPLEMENTOR / TESTER role agents) into a target platform repo. The pipeline is
driven by a Markdown task system, so an installed ai-builder turns tracked tasks
into shipped code.

**Last implemented:** Renamed `ai-builder` → `create-ai-builder` (it's a
generator, joins the `create-*` family) and **re-homed its task subsystem onto
the `create-project-system` generator** — stripped the 25 hand-built core scripts
to a task-free checkpoint, regenerated the decoupled machinery, and verified
parity against the 134 real tasks (writes, category grouping, worktree root, 175
`X-` subtasks all preserved).

**Focus / plan:**

- **Review + merge** the `task-system-generator-migration` branch on GitHub
  (pushed; machinery-swap-only diff, 28 files). Today's gate.
- After merge, **re-home** the create-ai-builder-owned follow-ups into this
  repo's now-working tracker (dogfooding): pipeline-script relocation, the
  repo-name rename audit, and target composition.
- Begin **target composition** — make `target/setup-project.sh` delegate the task
  layer to a pinned `create-project-system` `generate.sh` instead of copying.

```
task-system-generator-migration (pushed) ──review──▶ merge to main
                                                        │
                                                        ▼
              re-home 12/13/14 ──▶ target composition (pinned generate.sh)
```
