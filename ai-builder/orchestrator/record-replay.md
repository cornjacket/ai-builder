# Record / Replay

The orchestrator supports capturing a pipeline run as a git-based recording and
replaying it later without making any AI calls. This enables zero-cost
regression testing: run once, record, replay as many times as needed.

---

## Overview

**Record mode** (`--record-to DIR`) commits a snapshot of the regression
workspace to a git repository after every invocation. AI response text is
saved to `responses/inv-NN-ROLE.txt` so replay can serve the same response
without calling the AI. A `recording.json` manifest is written at the end
of the run.

**Replay mode** (`--replay-from DIR`) loads the manifest, checks for prompt
drift, and serves pre-recorded AI responses in order. Non-AI handlers
(DECOMPOSE_HANDLER, TESTER, LEAF_COMPLETE_HANDLER, etc.) re-run normally
against a freshly reset workspace. This keeps the test grounded: only the AI
outputs are fixed; routing and file operations are live.

---

## Capturing a Recording

```bash
python3 ai-builder/orchestrator/orchestrator.py \
    --job           path/to/README.md \
    --target-repo   sandbox/regressions/my-task/target \
    --output-dir    sandbox/regressions/my-task/output \
    --epic          main \
    --state-machine ai-builder/orchestrator/machines/builder/default.json \
    --record-to     sandbox/regressions/my-task \
    --record-branch my-task \
    --record-remote https://github.com/your-org/ai-builder-recordings.git
```

`--record-to DIR` — root of the recording git repository (created if absent).

`--record-branch BRANCH` — name of an orphan branch to create in the recording
repo. Orphan branches share the same remote but have completely independent
history, so each task gets its own namespace. Omit to use the default branch.

`--record-remote URL` — remote to add as `origin`. Used by `record.sh` to push
after the run completes. Omit if you only need a local recording.

After a successful run, push the recording to the remote:

```bash
git -C sandbox/regressions/my-task push --force origin my-task
```

See `tests/regression/user-service/record.sh` for a complete example.

---

## Replaying a Recording

```bash
python3 ai-builder/orchestrator/orchestrator.py \
    --job           path/to/README.md \
    --target-repo   sandbox/regressions/my-task/target \
    --output-dir    sandbox/regressions/my-task/output \
    --epic          main \
    --state-machine ai-builder/orchestrator/machines/builder/default.json \
    --replay-from   sandbox/regressions/my-task
```

`--replay-from DIR` — root of the recording git repository. The orchestrator
loads `recording.json`, queues the pre-recorded AI responses, and serves them
in order as the pipeline runs.

`--ignore-prompt-drift` — suppress the prompt drift warning and proceed with
replay even if role prompts have changed since the recording was captured. By
default the orchestrator prints a warning but still replays; use this flag to
silence the output.

`--record-to` and `--replay-from` are mutually exclusive.

If the recording was pushed to a remote, `test-replay.sh` will fetch it
automatically when no local copy is present.

See `tests/regression/user-service/test-replay.sh` for a complete example.

---

## Halting at N AI Invocations

```bash
python3 ai-builder/orchestrator/orchestrator.py \
    ... \
    --halt-after-ai-invocation 3
```

Stops the pipeline immediately after the Nth AI invocation completes (counting
only AI roles — ARCHITECT, IMPLEMENTOR — not internal handlers). The pipeline
exits 0 at that point; handlers that run before the halt (e.g. DECOMPOSE_HANDLER)
are not counted.

This is useful for stepping through a recording one AI stage at a time to
diagnose where a routing divergence occurs.

---

## Comparing a Snapshot Against the Output Directory

`compare_snapshot.py` diffs the recording's git commit at a given invocation
against the current working tree.

```bash
python3 ai-builder/orchestrator/compare_snapshot.py \
    --recording sandbox/regressions/my-task \
    --at        21 \
    --exclude   "output/execution.log" \
    --exclude   "output/logs" \
    --exclude   "target"
```

`--at N` — compare the working tree against the recording snapshot at
invocation N. Use the last invocation number from `recording.json` to check
the final state.

`--against M` — compare invocation N against invocation M instead of the
working tree. Useful for inspecting what a single invocation changed (pass N-1
and N).

`--exclude PATTERN` — exclude paths from the diff (repeatable). Uses git
pathspec exclusion. Always exclude `output/execution.log`, `output/logs`,
and orchestrator coordination files (`output/current-job.txt`,
`output/last-job.json`). When `task_hex_id` is stored in the manifest and
passed to `reset.sh` via `--task-id`, task directory paths are identical
between runs and `target/` can be included in the comparison — only the
Level:TOP `task.json` and `README.md` need exclusion (they contain
per-run timestamps and token counts).

Exit codes: `0` = no differences, `1` = differences found, `2` = error.

---

## Prompt Drift Detection

At record time, the orchestrator SHA-256 hashes each role prompt file and
stores the hashes in `recording.json` under `prompt_hashes`.

At replay time, the hashes are re-computed and compared. If any prompt has
changed, the orchestrator prints a warning listing the drifted files:

```
[recorder] WARNING: prompt drift detected — recording may not be valid:
  ai-builder/orchestrator/machines/builder/roles/IMPLEMENTOR.md
Use --ignore-prompt-drift to replay anyway.
```

A drifted prompt means the AI would likely produce a different response today
than it did at record time. The recording is still replayed (AI responses are
fixed), but the drift warning signals that the recording should be refreshed.

To refresh: re-run `record.sh` to capture a new recording with the updated
prompts, then push to the remote.

---

## The `recording.json` Manifest

Written to `<record-dir>/recording.json` at the end of a successful run.

```json
{
  "recorded_at": "2026-04-03T11:30:00.000000",
  "ai_builder_commit": "d983451...",
  "prompt_hashes": {
    "ai-builder/orchestrator/machines/builder/roles/ARCHITECT.md": "sha256:abc...",
    "ai-builder/orchestrator/machines/builder/roles/IMPLEMENTOR.md": "sha256:def..."
  },
  "invocations": [
    { "n": 1,  "role": "ARCHITECT",         "outcome": "ARCHITECT_DECOMPOSITION_READY", "commit": "a1b2c3d4...", "ai": true  },
    { "n": 2,  "role": "DECOMPOSE_HANDLER", "outcome": "HANDLER_SUBTASKS_READY",        "commit": "e5f6a7b8...", "ai": false },
    { "n": 3,  "role": "ARCHITECT",         "outcome": "ARCHITECT_DESIGN_READY",         "commit": "c9d0e1f2...", "ai": true  },
    ...
  ]
}
```

`ai_builder_commit` — git SHA of the ai-builder repo at record time (for
traceability).

`prompt_hashes` — SHA-256 of each role prompt file, keyed by repo-relative
path. Used for drift detection at replay time.

`invocations` — ordered list of every orchestrator invocation (AI + handlers).
Each entry has:
- `n` — invocation number (1-based, monotonically increasing)
- `role` — role name (e.g. `ARCHITECT`, `DECOMPOSE_HANDLER`)
- `outcome` — outcome token from the invocation
- `commit` — git SHA of the recording commit taken after this invocation
- `ai` — `true` for AI roles (ARCHITECT, IMPLEMENTOR), `false` for internal handlers

AI response files are stored at `<record-dir>/responses/inv-NN-ROLE.txt`.

`task_hex_id` — 6-char hex ID of the top-level user task (e.g. `"274b33"`).
Stored at record time; passed to `reset.sh --task-id` before replay so all
task directory names match the recording exactly, enabling `target/` to be
included in snapshot comparisons.
