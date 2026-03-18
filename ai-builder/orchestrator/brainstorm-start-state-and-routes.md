# Brainstorm: --start-state and --routes

Working document for `82c090-brainstorm-start-state-and-routes`.
Free-form notes, design experiments, and open questions.

---

## 1. What We're Solving

Two hardcoded values in the orchestrator block reuse:

| Hardcoded value | Location | Problem |
|-----------------|----------|---------|
| `current_role = "ARCHITECT"` | main loop | Can't resume at a different stage or test a specific role in isolation |
| `ROUTES = { ... }` | pipeline config | Can't change the state machine without editing source |

Both should be externalised as optional CLI flags with existing behaviour
as the default.

---

## 2. Current State Audit

### 2a. Start state

```python
current_role = "ARCHITECT"   # line 283 — hardcoded
```

There is no mechanism to override this. `TM_MODE` used to imply starting
at `TASK_MANAGER`, but that was removed when Oracle took over bootstrapping.

### 2b. ROUTES

Two dicts are built at startup:

```python
ROUTES = {                              # base (non-TM and TM shared)
    ("ARCHITECT",   "ARCHITECT_DESIGN_READY"):           "IMPLEMENTOR",
    ("ARCHITECT",   "ARCHITECT_NEED_HELP"):              None,
    ("IMPLEMENTOR", "IMPLEMENTOR_IMPLEMENTATION_DONE"):  "TESTER",
    ...
}

if TM_MODE:
    ROUTES.update({ ... })              # TM-specific additions
```

The lookup key is `(role, outcome)`. This is a flat dict today.

### 2c. `--request` — confirmed dead code

`--request` is parsed, validated, and read into `REQUEST`. That variable
is never passed to any prompt or function. The TM prompt builder has two
branches keyed on `last_outcome` (`ARCHITECT_DECOMPOSITION_READY` and
else). There is no cold-start branch for `last_outcome == ""`. Dead.

Lines to remove:
- argparse declaration (lines 38–41)
- path validation (lines 49–51)
- `REQUEST = ...` (line 72)
- startup log line (line 294)

---

## 3. `--start-state` Design

### 3a. CLI shape

```bash
python3 orchestrator.py \
    --target-repo ... \
    --output-dir  ... \
    --start-state TESTER        # override starting role
```

Optional. Default: `"ARCHITECT"` (preserves existing behaviour exactly).

### 3b. Validation

1. Role must exist in `AGENTS`. Fail fast with a clear error if not.
2. For roles that consume a job doc (ARCHITECT, IMPLEMENTOR, TESTER),
   a job doc must be locatable — either via `--job` (non-TM mode) or a
   pre-seeded `current-job.txt` (TM mode). Fail with a clear message if
   neither is present.
3. No validation that the start state is reachable from ROUTES — an
   unreachable start is not invalid, it just means the pipeline ends
   immediately on first `None` route (or `NEED_HELP`).

### 3c. Important: `--start-state TASK_MANAGER` is not a cold start

The task README says `--start-state` "restores the cold-start path."
That framing is misleading. Analysing the TM prompt builder:

- Branch 1: triggered when `last_outcome == "ARCHITECT_DECOMPOSITION_READY"`
- Branch 2: triggered for everything else (TESTER_TESTS_PASS)

If TM runs as the first role (`last_outcome == ""`), it falls into
Branch 2 — which instructs TM to run `on-task-complete.sh`. That's wrong
for a standing start.

**Conclusion:** `--start-state TASK_MANAGER` only makes sense if Oracle
has pre-seeded `current-job.txt` AND a third TM prompt branch is added
for `last_outcome == ""`. Without that third branch, starting at TM is
broken. This is a separate scope item — `--start-state` can be delivered
without solving it.

The useful cases for `--start-state` are:
- `TESTER` — re-run verification against existing implementation
- `IMPLEMENTOR` — resume after a failed implement step
- `ARCHITECT` — default, no change

`--start-state TASK_MANAGER` is an edge case that requires additional
TM prompt work. Flag as out of scope for this task.

### 3d. Implementation sketch

```python
# CLI
parser.add_argument(
    "--start-state",
    default="ARCHITECT",
    metavar="ROLE",
    help="Role to start the pipeline at (default: ARCHITECT)",
)

# Validation (after AGENTS is defined)
if args.start_state not in AGENTS:
    print(f"[orchestrator] Unknown start state '{args.start_state}'. "
          f"Valid roles: {list(AGENTS)}")
    sys.exit(1)

# Main loop
current_role = args.start_state    # replaces hardcoded "ARCHITECT"
```

---

## 4. `--routes` Design

### 4a. CLI shape

```bash
python3 orchestrator.py \
    --output-dir ... \
    --routes custom-routes.json
```

Optional. Default: built-in `ROUTES` dict (preserves existing behaviour).

### 4b. JSON format

Use the full outcome name as the key (matches what agents emit verbatim):

```json
{
  "ARCHITECT": {
    "ARCHITECT_DESIGN_READY":        "IMPLEMENTOR",
    "ARCHITECT_DECOMPOSITION_READY": "TASK_MANAGER",
    "ARCHITECT_NEEDS_REVISION":      "ARCHITECT",
    "ARCHITECT_NEED_HELP":           null
  },
  "IMPLEMENTOR": {
    "IMPLEMENTOR_IMPLEMENTATION_DONE": "TESTER",
    "IMPLEMENTOR_NEEDS_ARCHITECT":     "ARCHITECT",
    "IMPLEMENTOR_NEED_HELP":           null
  },
  "TESTER": {
    "TESTER_TESTS_PASS":  null,
    "TESTER_TESTS_FAIL":  "IMPLEMENTOR",
    "TESTER_NEED_HELP":   null
  }
}
```

Simplified outcome names (like `"DONE"`) were considered but rejected:
they create a mapping layer, break compatibility with `parse_outcome()`,
and require documentation of what each simplified name maps to. Full
names are unambiguous.

### 4c. Loading

```python
def load_routes(path: Path) -> dict:
    data = json.loads(path.read_text())
    routes = {}
    for role, transitions in data.items():
        for outcome, next_role in transitions.items():
            routes[(role, outcome)] = next_role
    return routes
```

### 4d. Validation

1. Valid JSON — fail on parse error.
2. All role keys must exist in `AGENTS`.
3. All next-role values (non-null) must exist in `AGENTS`.
4. Warn (not fail) if a role in `AGENTS` has no entries in the custom
   routes — it may be intentional (role unreachable in this pipeline).

### 4e. TM mode interaction — key decision

Currently when `TM_MODE` is true, `ROUTES.update({...})` appends
TM-specific transitions. If `--routes` is supplied, two options:

**Option A — Custom routes win entirely:** `--routes` replaces the
built-in table; TM mode additions are NOT applied on top. The caller
takes full responsibility for the state machine.

**Option B — TM mode additions still merge in:** even with `--routes`,
TM-specific transitions are added.

**Recommendation: Option A.** If you're supplying custom routes, you've
opted into full control. Silently adding TM-specific entries on top
would be surprising. If TM transitions are needed, include them in the
JSON file.

### 4f. `_NEED_HELP` handling

Currently `_NEED_HELP` outcomes are intercepted before the ROUTES lookup:

```python
if outcome.endswith("_NEED_HELP"):
    ...halt...
```

This should remain in place regardless of custom routes. Even if the
caller's routes JSON includes `_NEED_HELP` entries, the orchestrator
intercepts them first. This is not configurable behaviour — it's a
safety invariant.

### 4g. Implementation sketch

```python
# CLI
parser.add_argument(
    "--routes",
    type=Path,
    metavar="FILE",
    help="JSON file defining the pipeline route table (optional)",
)

# Loading (after AGENTS is defined)
if args.routes:
    ROUTES = load_routes(args.routes)
    # validate roles
    for (role, outcome), next_role in ROUTES.items():
        if role not in AGENTS:
            print(f"[orchestrator] routes: unknown role '{role}'")
            sys.exit(1)
        if next_role and next_role not in AGENTS:
            print(f"[orchestrator] routes: unknown next role '{next_role}'")
            sys.exit(1)
else:
    # existing ROUTES build logic (base + optional TM update)
    ...
```

---

## 5. `--request` Removal

Clean removal — no behaviour change, no replacement needed.

Files changed: `orchestrator.py` only.

Lines to delete:
```
parser.add_argument("--request", ...)           # lines 38-41
if args.request and not args.request.exists():  # lines 49-51
REQUEST = args.request.read_text() ...          # line 72
print(f"    request: ...")                       # line 294
```

After removal: `args.request` is gone, `REQUEST` is gone. No callers
to update — it was never consumed.

Update `orchestrator.md` to remove `--request` from docs.

---

## 6. Open Questions / Flags for Oracle

1. **`--start-state TASK_MANAGER` scope**: Confirm it is out of scope.
   Starting at TM cold requires a third TM prompt branch. Should this
   be a separate follow-on task?

2. **`--routes` and TM mode**: Confirm Option A (custom routes win
   entirely; TM additions are NOT merged in). This is the simpler,
   more explicit behaviour.

3. **`--routes` warning vs error for missing roles**: Should a role in
   AGENTS with no routes entry be a warning or a hard error? Current
   recommendation: warning (it may be intentional — the role is simply
   unreachable in this custom pipeline).

4. **File format for routes**: Confirm full outcome names (not
   simplified) in the JSON format.

---

## 7. Implementation Order

If Oracle approves:

1. Remove `--request` (isolated, zero-risk, no deps)
2. Add `--start-state` (simple substitution of one variable)
3. Add `load_routes()` helper + `--routes` flag + validation
4. Update `orchestrator.md` with new flags and routes JSON format
5. Regression test the three key scenarios

Items 1–2 are independent and could be a single pipeline subtask.
Item 3 is the bulk of the work. Items 4–5 follow naturally.
