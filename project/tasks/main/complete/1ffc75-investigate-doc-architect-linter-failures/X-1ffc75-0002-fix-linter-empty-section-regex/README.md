# Task: fix-linter-empty-section-regex

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 1ffc75-investigate-doc-architect-linter-failures             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Fix `_EMPTY_SECTION_RE` in `agents/doc/linter.py` so it only flags sections that
are truly empty (no content AND no sub-sections), not sections whose content is
organized entirely under sub-headings.

## Context

Root cause identified in brainstorm `sandbox/brainstorms/brainstorm-doc-architect-linter-failures.md`.

The current regex:
```python
_EMPTY_SECTION_RE = re.compile(
    r"^(#{1,6}\s+.+)\n+(?=#{1,6}\s|\Z)",
    re.MULTILINE,
)
```
fires on any heading followed (after blank lines) by ANY other heading — including
sub-headings (deeper `#` level). This causes false positives on well-structured docs
like:
```
## Public API

### Store interface
...
```
where `## Public API` is NOT empty — it contains subsections.

**Fix:** replace the regex with a line-scan function `_find_empty_sections(text)`
that only flags a heading as empty when the next non-blank line is a heading at the
SAME or HIGHER level (same or fewer `#`s) or when the heading is at EOF with nothing
after it.

Update `_check_file` to call `_find_empty_sections` instead of the regex.

Also update `linter.md` companion doc to reflect the corrected check behaviour.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
