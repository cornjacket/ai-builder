# Sandbox

Temporary brainstorming documents. This directory is a scratchpad — nothing here is permanent or version-controlled (except this README).

## Rules

- **Files here are not committed to git.** The `.gitignore` silently excludes everything except this README — files will not appear in `git status` and will not survive a fresh clone. This is intentional.
- **Move valuable content out only when ready.** If a brainstorm produces something worth keeping, promote it to the appropriate location (`docs/`, `project/tasks/`, `roles/`, etc.) — but only once the content is properly structured for that destination. Do not move a brainstorm to `docs/` just to get it committed; premature promotion adds noise and gives unfinished thinking false authority.
- **Never use sandbox for task implementation.** Sandbox content is temporary and verbose — it bypasses the task document requirement. All feature implementation must go through `tasks/` with a proper task document.
- **Why not version-control brainstorms?** Brainstorming artifacts become noise for AI agents that index the repo. Keeping this directory clean ensures AI context stays focused on authoritative documents.
