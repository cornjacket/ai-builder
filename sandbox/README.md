# Sandbox

Scratchpad for brainstorming and regression test artefacts. Nothing here is
permanent or version-controlled (except this README and the `regressions/`
directory structure).

## Layout

```
sandbox/
  brainstorms/          # brainstorm-*.md files — design discussions and explorations
  regressions/          # live working dirs for regression test runs
    <name>/
      output/           # AI-generated artefacts (docs, built code)
      target/           # task management repo for the pipeline run
  <other>/              # miscellaneous experiments (not regressions)
```

Each regression in `tests/regression/<name>/` uses
`sandbox/regressions/<name>/output/` and `sandbox/regressions/<name>/target/`
as its working directories. `reset.sh` creates/wipes these; `run.sh` points the
orchestrator at them.

## Rules

- **Files here are not committed to git.** The `.gitignore` silently excludes
  everything except this README — files will not appear in `git status` and will
  not survive a fresh clone. This is intentional.
- **Move valuable content out only when ready.** If a brainstorm produces
  something worth keeping, promote it to the appropriate location (`docs/`,
  `project/tasks/`, `roles/`, etc.) — but only once the content is properly
  structured for that destination.
- **Never use sandbox for task implementation.** All feature implementation must
  go through `tasks/` with a proper task document.
- **Why not version-control brainstorms?** Brainstorming artifacts become noise
  for AI agents that index the repo. Keeping this directory clean ensures AI
  context stays focused on authoritative documents.
