# list-tasks.sh

Lists tasks in an epic, grouped by status folder. Reads task ordering and
completion state from each `README.md` so the output matches the same
convention as the on-disk task system. Top-level tasks are always shown;
checked-off subtask entries (`[x]`) are hidden by default and surfaced
with `--all`.

---

## CLI Flags

| Flag | Description |
|------|-------------|
| `--epic <name>` | Epic to list (default: `main`). |
| `--folder <status>` | Limit output to a single status folder (`inbox`, `draft`, `backlog`, `in-progress`, `complete`, `wont-do`). Omit to show all. |
| `--depth <n>` | Recursion depth for subtasks (default: `1` — top-level tasks only). |
| `--root <path>` | Traverse from a specific path instead of an epic. Path is relative to `project/tasks/`. |
| `--all` | Include completed `[x]` subtask entries in subtask listings. |
| `--tag <tag>` | Filter to tasks whose `Tags` field contains the given value (case-insensitive). |
| `--category <branch>` | Filter to tasks whose `Category` field equals the given worktree-class branch (e.g. `task-tooling`). Use `unclassified` to match tasks with `Category: —` or no Category field. |
| `--group-by-category` | Within each status folder, group tasks under `[<category>]` sub-headings in the canonical class order. The `unclassified` group always trails. |
| `--sort-priority` | Order tasks `HIGH → MED → LOW → unset` within each folder (or each category group, when combined with `--group-by-category`). |

`--category` and `--group-by-category` apply only at the top-level
(depth-1) layer — subtasks inherit category from their parent and don't
carry the field themselves.

---

## Category Order

When grouping is enabled, categories are listed in the order they appear
in [`project/tasks/classes.md`](../classes.md):

1. `gemini-compat`
2. `orchestrator-core`
3. `acceptance-spec`
4. `new-pipelines`
5. `regression-infra`
6. `task-tooling`
7. `docs`
8. `workspace-mgmt`
9. `unclassified` (always last)

The order is hard-coded in `CATEGORY_ORDER` at the top of the script. If
`classes.md` reorders or adds a class, update both files together.

---

## Examples

```bash
# Outstanding work, all folders
list-tasks.sh --epic main --folder draft --depth 2
list-tasks.sh --epic main --folder backlog --depth 2
list-tasks.sh --epic main --folder in-progress --depth 2

# Priority-ordered backlog
list-tasks.sh --epic main --folder backlog --sort-priority

# What's next per worktree class — global view
list-tasks.sh --epic main --folder backlog --group-by-category --sort-priority

# What's next for a specific worktree
list-tasks.sh --epic main --folder backlog --category task-tooling --sort-priority

# Tasks missing a Category field
list-tasks.sh --epic main --folder backlog --category unclassified
```

---

## Implementation Notes

- `get_priority` and `get_category` parse the task's `README.md` table
  with line-anchored `grep` patterns (`^| Priority`, `^| Category`).
- The category filter is applied in both `print_status_tasks` (for the
  default depth-1 view) and `print_dir_tasks` (only when `current_depth`
  is 1, so deeper recursion never re-applies the filter).
- Group rendering iterates `CATEGORY_ORDER` outer and `task_dirs` inner.
  Per-task printing is duplicated between the grouped and ungrouped
  branches; this is deliberate to keep the indentation logic obvious.
- Tests live alongside the generated subsystem (see the target repo test suite).
