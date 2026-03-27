---
Purpose: Build a master documentation index from a pipeline output directory tree.
Tags: orchestrator, documentation, pipeline
---

# build_master_index.py

Walks an output directory, extracts `Purpose:` and `Tags:` from every `.md`
file (excluding `master-index.md` and the root-level `README.md`), and
produces a single index file with header depth mirroring directory depth.

Component-level `README.md` files in subdirectories **are included** — ARCHITECT
writes those with `Purpose:`/`Tags:` headers and they are the primary indexed docs.

Intended for companion documentation files (e.g. `store.md`, `data-flow.md`)
written by ARCHITECT or IMPLEMENTOR alongside source code.

## Inputs

| Parameter | Type | Description |
|-----------|------|-------------|
| `output_dir` | `Path` | Root of the pipeline output directory |
| `dest` | `Path \| None` | Destination file; defaults to `output_dir/master-index.md` |

## Outputs

Writes `master-index.md` at `dest`. Overwrites the generated sections while
preserving any user sentinel blocks from a previous run.

## User sentinel blocks

Human-added content between `<!-- user-doc-start -->` and `<!-- user-doc-end -->`
markers is preserved across rebuilds. Blocks are keyed to their enclosing
section heading.

## Output format

```markdown
# output-dir-name

### store
| File | Tags | Description |
|------|------|-------------|
| store.md | architecture, design | Thread-safe in-memory user store. |

### handlers
| File | Tags | Description |
| api.md | architecture, design | HTTP handlers for the user management API. |
```

## CLI usage

```bash
python3 build_master_index.py --output-dir path/to/output [--dest path/to/master-index.md]
```

## In-process usage

```python
from build_master_index import build_master_index
build_master_index(output_dir, dest)
```

## Orchestrator integration

Called at pipeline completion as part of the post-completion flow (subtask 0021).
