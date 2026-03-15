# Task: add-next-subtask-script

| Field       | Value                               |
|-------------|-------------------------------------|
| Status | complete |
| Epic        | main                                |
| Tags        | —                                   |
| Parent      | 452116-optimize-tm-agent-prompt     |
| Priority    | —                                   |
| Complexity  | atomic                              |
| Stop-after  | false                               |
| Last-task   | false                               |

## Goal

Create `next-subtask.sh` — a script that prints the absolute path of the next
incomplete subtask README under a given parent task, or exits non-zero if none
remain.

## Context

The TM agent currently identifies the next subtask to work on by running
`list-tasks.sh` and parsing its output. This is fragile. A dedicated script
encapsulates the logic and gives the TM agent a clean, reliable tool to call.

## Design

```bash
next-subtask.sh --epic <epic> --folder <status> --parent <parent-id-name>
```

- Reads the parent task's README subtask list (between `<!-- subtask-list-start -->`
  and `<!-- subtask-list-end -->`)
- Finds the first entry that is `- [ ]` (incomplete)
- Extracts the subtask directory name from the entry (linked or plain format)
- Prints the absolute path to that subtask's `README.md`
- Exit 0 if a next subtask was found, exit 1 if all subtasks are complete or
  the list is empty

Must be added to both `project/tasks/scripts/` and `target/project/tasks/scripts/`.

## Acceptance Criteria

1. Given a parent with incomplete subtasks, prints the correct absolute path
   and exits 0
2. Given a parent where all subtasks are complete, exits 1 with no output
3. Given a parent with a mix of complete and incomplete, returns the first
   incomplete one (top of list)
4. Works for both linked format (`- [ ] [name](name/)`) and plain format
   (`- [ ] name`)

## Suggested Tools

```bash
bash project/tasks/scripts/next-subtask.sh --epic main --folder in-progress --parent <task>
```

## Notes

_None._
