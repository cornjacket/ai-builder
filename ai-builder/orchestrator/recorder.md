# recorder.py

Python module providing record and replay support for the pipeline orchestrator.
Imported as `recorder_mod` in `orchestrator.py`.

For the user-facing guide (flags, workflow, snapshot comparison), see
[`record-replay.md`](record-replay.md).

---

## Design

The module is split into three concerns:

1. **Record** — after each orchestrator invocation, commit a git snapshot of
   the regression workspace. AI responses are written to `responses/` so replay
   can serve them verbatim. A `recording.json` manifest is written and committed
   at run end.

2. **Replay** — load the manifest, detect prompt drift, and return the queued
   AI responses. The orchestrator calls these at startup; the responses are
   served in order as the pipeline runs.

3. **Workspace restoration** — during replay, after serving a pre-recorded AI
   response for a role that writes to `output/` (e.g. IMPLEMENTOR), restore
   `output/` from the recording snapshot at that invocation. Without this, live
   handlers (TESTER) would see an empty `output/` and fail.

The recording directory is a git repository. Each commit message is
`inv-NN ROLE OUTCOME`, making the commit log a human-readable trace of the
pipeline run.

---

## API

### Record mode

```python
init(record_dir, branch=None, remote_url=None)
```
Initialize a git repo in `record_dir` if one does not already exist. Creates
an orphan branch if `branch` is given. Adds `remote_url` as `origin` if given.
Returns immediately if `.git` already exists — callers must wipe `.git` before
calling `init` when re-recording (see `record.sh`).

```python
commit(record_dir, n, role, outcome, response=None) -> str
```
Stage all changes and commit. Returns the commit SHA. If `response` is provided
(AI invocations only), writes it to `responses/inv-{n:02d}-{role}.txt` before
staging. Uses `--allow-empty` so handler invocations that produce no file
changes still get a commit, keeping the invocation index in sync with the
manifest.

```python
write_manifest(record_dir, invocations, role_prompts, repo_root, task_hex_id=None)
```
Write `recording.json` to `record_dir` and commit it. Must be called after the
final `commit()` call — it adds one more commit on top. Fields written:
- `recorded_at` — ISO timestamp
- `ai_builder_commit` — git SHA of the ai-builder repo at record time
- `task_hex_id` — if provided, stored for replay to pin task directory names
- `prompt_hashes` — SHA-256 of each role prompt file (keyed by repo-relative path)
- `invocations` — the ordered list passed in

### Replay mode

```python
load_manifest(record_dir) -> dict
```
Load and return `recording.json`. Raises `FileNotFoundError` if absent.

```python
check_prompt_drift(manifest, role_prompts, repo_root) -> list[str]
```
Return a list of prompt file paths that have changed since the recording was
captured. Empty list = no drift, safe to replay. Only checks prompts present
in both the manifest and `role_prompts` — new or removed prompts are not
flagged.

```python
load_ai_responses(record_dir, manifest) -> list[tuple[int, str, str]]
```
Return an ordered list of `(n, role, response_text)` for all AI invocations in
the manifest. Raises `FileNotFoundError` if any response file is missing.

### Workspace restoration

```python
restore_output(record_dir, n, exclude=None)
```
Restore `output/` from the recording commit at invocation N using
`git checkout <sha> -- output/`. Called during replay after serving a
pre-recorded AI response for a non-ARCHITECT role.

`exclude` is a list of git pathspecs to skip (e.g.
`["output/current-job.txt", "output/last-job.json", "output/execution.log",
"output/handoff-state.json", "output/logs"]`). Orchestrator coordination
files must always be excluded — they contain live run state (current hex IDs,
active job paths) that must not be overwritten with recording-era values.

Only `output/` is restored. `target/` is left untouched because it contains
fresh hex-prefixed task paths that differ between runs.

### Snapshot comparison (utility)

```python
diff_snapshot(record_dir, at_n, against_n=None, exclude_paths=None) -> str
```
Return a unified diff of the recording at invocation N against the working
tree (or invocation M if `against_n` is given). Empty string = no differences.
Used by `compare_snapshot.py`; prefer that script for CLI usage.

---

## Assumptions

- The recording directory must be separate from `output/` and `target/`. If
  nested inside either, `git add -A` would capture the recording's own files
  as part of the snapshot, and `compare_snapshot.py` diffs would include
  spurious changes from the recording's own state.
- `init()` is idempotent when `.git` already exists — it returns immediately.
  Re-recording requires the caller to wipe `.git` first (done by `record.sh`).
- `commit()` uses `--allow-empty` deliberately. Every invocation gets a commit,
  whether or not any files changed. This keeps `n` in the manifest aligned with
  commit positions in the git log.
- `write_manifest()` makes one additional commit after being called. The manifest
  is always the final commit in the recording.
