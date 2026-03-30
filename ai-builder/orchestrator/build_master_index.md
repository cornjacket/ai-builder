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

Section header depth mirrors directory depth relative to the output root
(`##` for the shallowest dirs, `###` one level deeper, capped at `####`).
Every filename in a table is a relative hyperlink from the index to the file.

```markdown
# output-dir-name

## internal/userservice
| File | Tags | Description |
|------|------|-------------|
| [README.md](internal/userservice/README.md) | architecture, design | Composite overview of the userservice package. |
| [theory-of-operation.md](internal/userservice/theory-of-operation.md) | architecture, design | Data-flow diagram for the userservice layer. |

### internal/userservice/handlers
| File | Tags | Description |
|------|------|-------------|
| [README.md](internal/userservice/handlers/README.md) | architecture, design | HTTP handlers for the user management API. |
| [api.md](internal/userservice/handlers/api.md) | architecture, design | Full HTTP API contract. |

### internal/userservice/store
| File | Tags | Description |
|------|------|-------------|
| [store.md](internal/userservice/store/store.md) | architecture, design | Thread-safe in-memory user store. |
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
