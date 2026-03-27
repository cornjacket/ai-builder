# Task: master-index-rebuild-script

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 49352f-redesign-pipeline-communication-architecture             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Write a `build-master-index.py` script that traverses the output directory
tree, extracts `Purpose:` and `Tags:` from every `.md` file, and produces a
combined documentation index with header depth mirroring directory depth.
Preserve any user sentinel blocks from a previous index run.

## Context

After a full pipeline run the output directory contains documentation files
produced by ARCHITECT and IMPLEMENTOR at every level of the component tree.
There is currently no consolidated view across all of them. The master index
provides this — a single file the human can navigate to understand the whole
system.

**Algorithm:**
1. Walk the output directory tree from the top
2. For each `.md` file encountered (excluding `README.md` and `master-index.md`):
   - Extract first sentence of `Purpose:` section
   - Extract `Tags:` field
3. Organise entries by directory depth — each directory level becomes a
   header level in the index
4. Render the index:
   ```markdown
   # user-service

   ## store
   | File | Tags | Description |
   |------|------|-------------|
   | data-flow.md | architecture, design | How requests flow... |

   ## handlers
   | File | Tags | Description |
   | ...

   ### handlers/login
   | ...
   ```

**User sentinel blocks:**
If a previous `master-index.md` exists, preserve any content between
`<!-- user-doc-start -->` and `<!-- user-doc-end -->` markers. These are
human-added annotations that survive rebuilds.

**Usage:**
```bash
python3 build-master-index.py --output-dir path/to/output --dest master-index.md
```

Runs as the final post-completion step after README render (subtask 0012).
Wired into the orchestrator via subtask 0010.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
