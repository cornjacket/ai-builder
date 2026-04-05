# Regression Tests

End-to-end tests for the ai-builder pipeline. Each test runs the full
orchestrator against a real job spec, verifies routing, and confirms the
generated output with a gold test suite.

---

## Two Modes: Replay vs Live

Every regression test supports two run modes. **Choosing the right one
matters** — they answer different questions and have very different costs.

### Replay (default — use this most of the time)

```bash
bash tests/regression/<name>/test-replay.sh
```

Serves pre-recorded AI responses instead of calling the AI. Only internal
handlers (DECOMPOSE_HANDLER, TESTER, LEAF_COMPLETE_HANDLER) run live. The
recording is a git repo of workspace snapshots captured during a prior live
run — replay checks out the recorded AI outputs at the right moments so
handlers see the same files they saw during recording.

**Use replay when:**
- Verifying orchestrator logic, handler scripts, or task management scripts
  after a code change
- Running in CI or as a pre-merge check
- You want deterministic, fast, zero-cost verification
- The role prompts have not changed since the recording was captured

**What replay verifies:**
- Routing path (same role/outcome sequence as the recording)
- Output artifacts (Go source files match the recording snapshot)
- Task tree state (component subtask directories, X- renames, design/AC in task.json)

**What replay does NOT verify:**
- Whether the AI still produces correct code for this spec today
- Whether prompt changes produce good results

### Live (re-record — use sparingly)

```bash
bash tests/regression/<name>/run.sh [--force]
```

Runs the full pipeline with real AI calls, captures a new recording, and
pushes it to the remote. Costs API tokens (10–30 min, depending on test
complexity). Use this to refresh the recording after prompt changes or when
the replay test diverges from expected behaviour.

**Use live when:**
- Role prompts have changed (prompt drift detected by replay)
- You want to verify the AI still produces working code for this spec
- Creating a new regression test for the first time
- Investigating a suspected regression in AI output quality
- The old recording is stale and replay is failing for the wrong reasons

**After a live run:** run `test-replay.sh` once to confirm the new recording
replays cleanly before treating it as the new baseline.

---

## How Record/Replay Works

The mechanism is not obvious — it is worth understanding before debugging a
failing replay.

### Record mode

```
                    ┌─── orchestrator ──────────────────────────────────┐
                    │                                                    │
job doc ──────────► │  inv-01  ACCEPTANCE_SPEC_WRITER/claude ─────────► │ ──► AI call
                    │                                        response    │
                    │  [recorder] git commit inv-01 ◄─────────────────  │
                    │            saves response to responses/inv-01-ACCEPTANCE_SPEC_WRITER.txt
                    │                                                    │
                    │  inv-02  ARCHITECT/claude ──────────────────────► │ ──► AI call
                    │                                        response    │
                    │  [recorder] git commit inv-02                      │
                    │            saves response to responses/inv-02-ARCHITECT.txt
                    │                                                    │
                    │  inv-03  DECOMPOSE_HANDLER/internal ─────────────► │ (no AI)
                    │                                                    │
                    │  [recorder] git commit inv-03                      │
                    │                                                    │
                    │  inv-04  ARCHITECT/claude ──────────────────────► │ ──► AI call
                    │                                        response    │
                    │  [recorder] git commit inv-04                      │
                    │            saves response to responses/inv-04-ARCHITECT.txt
                    │  ...                                               │
                    │  [recorder] write recording.json manifest          │
                    └────────────────────────────────────────────────────┘

Recording repo (sandbox/regressions/<name>/):
  ├── recording.json          manifest: invocation list, prompt hashes, task hex ID
  ├── responses/
  │   ├── inv-01-ARCHITECT.txt
  │   ├── inv-03-ARCHITECT.txt
  │   └── inv-05-IMPLEMENTOR.txt   (one file per AI invocation)
  ├── output/                 snapshot of pipeline output at each commit
  └── target/                 snapshot of task tree at each commit
```

### Replay mode

```
                    ┌─── orchestrator ──────────────────────────────────┐
recording.json ───► │  loads manifest, queues AI responses              │
                    │                                                    │
                    │  inv-01  ACCEPTANCE_SPEC_WRITER/claude             │
                    │  ← serves responses/inv-01-ACCEPTANCE_SPEC_WRITER.txt  no AI call
                    │                                                    │
                    │  inv-02  ARCHITECT/claude                          │
                    │  ← serves responses/inv-02-ARCHITECT.txt          │  no AI call
                    │                                                    │
                    │  inv-03  DECOMPOSE_HANDLER/internal ─────────────► │  runs live
                    │          creates subtask dirs in target/           │
                    │                                                    │
                    │  inv-04  ARCHITECT/claude                          │
                    │  ← serves responses/inv-04-ARCHITECT.txt          │  no AI call
                    │                                                    │
                    │  inv-05  DOCUMENTER_POST_ARCHITECT/internal ──────► │  runs live
                    │                                                    │
                    │  inv-06  IMPLEMENTOR/claude                        │
                    │  ← serves responses/inv-06-IMPLEMENTOR.txt        │  no AI call
                    │  [recorder] git checkout inv-06 -- output/        │
                    │            restores Go source files IMPLEMENTOR   │
                    │            wrote so TESTER can find them          │
                    │                                                    │
                    │  inv-07  SPEC_COVERAGE_CHECKER/internal ──────────► │  runs live
                    │          verifies test coverage of acceptance-spec │
                    │                                                    │
                    │  inv-08  TESTER/internal ────────────────────────► │  runs live
                    │          builds and tests restored source files    │
                    │  ...                                               │
                    └────────────────────────────────────────────────────┘
```

**Key insight:** the AI's text response is served verbatim, but it doesn't
re-execute the file writes. The recorder restores `output/` from the git
snapshot after each non-ARCHITECT AI invocation so that live handlers
(TESTER, LEAF_COMPLETE_HANDLER) operate on the same files they saw during
the recording.

**Why task hex IDs are pinned:** the recording commits contain `target/`
with hex-prefixed task directories (`274b33-user-service/`, etc.). To
compare the task tree against the recording, the replay must produce the
same paths. The manifest stores `task_hex_id` and `reset.sh` is called with
`--task-id` to reproduce it. Only the Level:TOP `task.json` and `README.md`
are excluded from the snapshot comparison — they contain per-run timestamps
and token counts that are always different.

---

## Tests

| Test | Pipeline mode | What it exercises |
|------|--------------|-------------------|
| [fibonacci](fibonacci/) | Simple (non-TM) | Single atomic job: ARCHITECT → IMPLEMENTOR → TESTER |
| [user-service](user-service/) | TM builder | Single-level decompose: one service into atomic components |
| [platform-monolith](platform-monolith/) | TM builder | Multi-level decompose: platform → two services → sub-components |
| [doc-user-service](doc-user-service/) | TM doc | Doc pipeline: 2-level decomposition, atomic leaf documentation |
| [doc-platform-monolith](doc-platform-monolith/) | TM doc | Doc pipeline: 3-level decomposition, integrate nodes |

Each test has its own `README.md` with full specification, run instructions,
and expected pipeline routing.

---

## Common Pattern

All three tests follow the same structure:

```
tests/regression/<name>/
    gold/           committed reference tests — never visible to the pipeline
    reset.sh        wipes previous output, archives the run, sets up fresh state
    README.md       test specification and run instructions
    runs/           timestamped run archives (execution.log, task.json, README.md)
    last_run -> runs/YYYY-MM-DD-HH-MM-SS/   symlink to most recent run
```

### gold/ separation

Gold tests are committed reference tests that run after the pipeline completes.
The pipeline agent (TESTER) has no visibility into `gold/` — its working
directory is the output directory. Gold tests verify the generated code
independently against known-correct cases.

This separation ensures the pipeline cannot "cheat" by copying the gold tests
rather than deriving its own from the Acceptance Criteria.

### Run order

For every test:

1. **Reset** — `tests/regression/<name>/reset.sh`

   Archives the previous run (if any) to `runs/YYYY-MM-DD-HH-MM-SS/` with
   `execution.log`, `task.json`, and `README.md` from the Level:TOP task.
   Wipes the output and (for TM tests) target repo directories. Sets up fresh
   state for the next run.

2. **Run the pipeline** — see the test's own README for the exact command.

3. **Run the gold test** — `cd tests/regression/<name>/gold && go test -tags regression ./...`

### Run history

`reset.sh` appends a summary row to `runs/run-history.md` after each run.
Columns: run number, date, elapsed time, token counts per role
(ARCHITECT, IMPLEMENTOR, TESTER).

---

## fibonacci — Simple mode

The simplest test. Uses `--job` (non-TM) mode — a single job document fed
directly to the pipeline without a target repo or task system.

Tests the three-phase baseline: ARCHITECT fills in Design + Acceptance
Criteria, IMPLEMENTOR writes `fibonacci.go`, TESTER verifies it.

See [`fibonacci/README.md`](fibonacci/README.md) for full details.

---

## user-service — TM single-level decomposition

Exercises the full TM decomposition loop. The pipeline is given only a
high-level service specification; ARCHITECT decides the component breakdown.
DECOMPOSE_HANDLER creates the subtask tree; each component goes through its
own ARCHITECT → IMPLEMENTOR → TESTER cycle; LEAF_COMPLETE_HANDLER traverses
the tree.

See [`user-service/README.md`](user-service/README.md) for full details.

---

## platform-monolith — TM multi-level decomposition

The most complex test. A two-service monolith where one service (IAM)
itself decomposes into sub-components. Exercises the full multi-level tree
traversal: nested DECOMPOSE_HANDLER passes, INTERNAL-level integrate steps,
and a final TOP-level integrate that wires everything together.

See [`platform-monolith/README.md`](platform-monolith/README.md) for full details.
