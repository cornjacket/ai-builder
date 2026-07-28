# Daily plan — 2026-07-28

**What this repo is (for a newcomer):** `create-ai-builder` is a generator that
installs an AI-agent **build pipeline** (an orchestrator plus ARCHITECT /
IMPLEMENTOR / TESTER role agents) into a target platform repo. The pipeline is
driven by a Markdown task system, so an installed ai-builder turns tracked tasks
into shipped code.

**Last implemented:** the `task-system-generator-migration` branch **merged to
main** (PR #4) — the task subsystem now rides on the `create-project-system`
generator instead of the 25 hand-built scripts. The three create-ai-builder-owned
follow-ups were then **re-homed into this repo's own tracker** (dogfooding the
migrated tooling): `29297c-relocate-pipeline-scripts` (task-tooling, MED),
`59ea60-repo-name-rename-audit` (workspace-mgmt, LOW), and
`15d940-target-setup-uses-generator-for-tasks` (workspace-mgmt, MED — renamed from
the old `target-composition-delegate-to-generate`).

**Focus / plan:**

- **Begin target composition — `15d940-target-setup-uses-generator-for-tasks`.**
  Make `target/setup-project.sh` **delegate** the task layer to a pinned
  `create-project-system` `generate.sh` instead of copying create-ai-builder's own
  scripts. Start the task (move to `in-progress`, worktree class `workspace-mgmt`),
  describe subtasks, and align before implementing.
- Design the pin: which `create-project-system` ref to pin to, and how the target
  setup invokes `generate.sh` (`--tasks-dir` / `--epic` / `--with-status`).
- Next in the re-homed queue (not today): `29297c-relocate-pipeline-scripts`
  (MED), then `59ea60-repo-name-rename-audit` (LOW).

```
PR #4 merged ─▶ follow-ups re-homed ─▶ [15d940] target composition (today)
                                          │  setup-project.sh delegates to
                                          │  a pinned create-project-system generate.sh
                                          ▼
                            then ▶ 29297c relocate pipeline scripts ▶ 59ea60 rename audit
```
