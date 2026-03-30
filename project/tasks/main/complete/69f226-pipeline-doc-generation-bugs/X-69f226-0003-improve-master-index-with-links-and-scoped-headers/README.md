# Task: improve-master-index-with-links-and-scoped-headers

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 69f226-pipeline-doc-generation-bugs             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Rewrite `build_master_index.py` so the generated `master-index.md` uses scoped
headers mirroring the directory hierarchy and includes hyperlinks to every referenced
file rather than bare filenames.

## Context

The current `master-index.md` is a flat table per directory with no links:

```markdown
##### internal/userservice/handlers
| File | Tags | Description |
| README.md | architecture, design | HTTP handlers ... |
```

Files are not clickable. The header depth (`#####`) is arbitrary and not navigable.

**Required output format:**

```markdown
# Output Index

## internal/userservice

### handlers
| File | Tags | Description |
|------|------|-------------|
| [README.md](internal/userservice/handlers/README.md) | architecture, design | HTTP handlers ... |
| [api.md](internal/userservice/handlers/api.md) | architecture, design | Full HTTP API contract. |

### store
| File | Tags | Description |
|------|------|-------------|
| [README.md](internal/userservice/store/README.md) | architecture, design | Thread-safe in-memory CRUD store. |
```

**Rules:**
- Header depth mirrors directory depth relative to the output root (1 = `#`, 2 = `##`, etc.), capped at `####`
- Every filename in the table is a relative hyperlink from the index to the file
- Composite-level READMEs (from 0002) appear in their directory's table like any other `.md` file
- Preserve the `<!-- user-doc-start/end -->` guard for user-added content

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
