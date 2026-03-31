# agents/documenter.py

`DocumenterAgent` — scans the output directory for companion `.md` files and
rebuilds the `## Documentation` section in `README.md`.

## run(job_doc, output_dir, **kwargs)

**Inputs:**
- `job_doc: Path` — path to the task's `README.md`; `task.json` is resolved as
  a sibling
- `output_dir: Path` — directory scanned for `*.md` files (excluding `README.md`)

**Reads:**
- `task.json["documents_written"]` — if `false` or absent, returns immediately
- `*.md` files in `output_dir` — looks for `Purpose:` and `Tags:` headers

**Writes:** `output_dir/README.md` — replaces or appends the `## Documentation`
section with a table of design and implementation docs.

**Returns `AgentResult` with `OUTCOME: DOCUMENTER_DONE`** in all non-error cases.

**Tag routing:** files with `Tags: implementation` are listed under
`### Implementation Notes`; all others under `### Design`.

## Context dependency

None. `DocumenterAgent` takes no constructor arguments.
