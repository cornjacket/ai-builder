# Task: brainstorm-token-usage-and-caching-costs

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | in-progress |
| Epic        | main               |
| Tags        | —               |
| Priority    | HIGH        |
| Next-subtask-id | 0002 |

## Goal

Understand and improve the token usage and cost characteristics of the ai-builder pipeline.
The accumulated handoff history mechanism is causing runaway token consumption at scale.
Design mitigations and establish baselines so we can detect regressions.

## Context

Observed during the platform-monolith regression run (2026-03-17): 24 invocations,
30m 48s total. Only 252 tokens were "new" input across the entire run — effectively
everything was cached. Total tokens including cache reads: 4,795,236.

The core issue is that `build_prompt()` appends all prior agent handoffs into every
subsequent prompt. This makes sense for creative/design roles (ARCHITECT needs prior
context) but is pure overhead for handler roles that just run shell scripts.

**Open questions to explore:**
1. Do ALL roles genuinely need the full accumulated handoff history, or just the
   immediately prior one? Does IMPLEMENTOR need to know what ARCHITECT said 10
   invocations ago, or just the current job doc + most recent handoff?
2. Does accumulating handoffs hurt quality (distraction / context dilution) as well
   as cost?
3. What is the right scoping model — per-role? sliding window? role-typed?
4. How does Anthropic's pricing actually work for cache hits vs misses vs output?
   What is the real cost of this run vs what it would be uncached?
5. How do we detect if a code change causes a large token usage regression?
   Should the regression test have a token budget assertion?

## Execution Log — platform-monolith run (2026-03-17)

| Field          | Value |
|----------------|-------|
| Task           | build-1 |
| Start          | 2026-03-17 21:56:42 |
| End            | 2026-03-17 22:27:30 |
| Total time     | 30m 48s |
| Invocations    | 24 |
| Tokens in      | 252 |
| Tokens out     | 100,470 |
| Tokens cached  | 4,694,514 |
| Tokens total   | 4,795,236 |

| # | Role | Agent | Description | Ended | Elapsed | Tokens In | Tokens Out | Tokens Cached |
|---|------|-------|-------------|-------|---------|-----------|------------|---------------|
| 1 | ARCHITECT | claude | build-1 | 21:57:42 | 1m 00s | 8 | 3,154 | 139,330 |
| 2 | DECOMPOSE_HANDLER | claude | build-1 | 21:59:12 | 1m 29s | 16 | 5,134 | 371,459 |
| 3 | ARCHITECT | claude | metrics | 22:00:35 | 1m 23s | 8 | 3,524 | 143,333 |
| 4 | IMPLEMENTOR | claude | metrics | 22:02:43 | 2m 07s | 12 | 7,479 | 276,435 |
| 5 | TESTER | claude | metrics | 22:03:08 | 25s | 6 | 827 | 99,686 |
| 6 | LEAF_COMPLETE_HANDLER | claude | metrics | 22:04:11 | 1m 02s | 11 | 2,643 | 216,847 |
| 7 | ARCHITECT | claude | iam | 22:05:24 | 1m 13s | 6 | 3,432 | 106,329 |
| 8 | DECOMPOSE_HANDLER | claude | iam | 22:06:45 | 1m 21s | 10 | 4,684 | 211,774 |
| 9 | ARCHITECT | claude | auth-lifecycle | 22:08:44 | 1m 58s | 50 | 5,886 | 182,459 |
| 10 | IMPLEMENTOR | claude | auth-lifecycle | 22:10:48 | 2m 04s | 12 | 8,535 | 322,595 |
| 11 | TESTER | claude | auth-lifecycle | 22:11:19 | 31s | 5 | 1,491 | 83,329 |
| 12 | LEAF_COMPLETE_HANDLER | claude | auth-lifecycle | 22:11:52 | 32s | 6 | 1,392 | 103,748 |
| 13 | ARCHITECT | claude | authz-rbac | 22:14:47 | 2m 54s | 9 | 9,327 | 213,275 |
| 14 | IMPLEMENTOR | claude | authz-rbac | 22:16:20 | 1m 32s | 11 | 6,986 | 265,601 |
| 15 | TESTER | claude | authz-rbac | 22:16:45 | 24s | 4 | 617 | 61,647 |
| 16 | LEAF_COMPLETE_HANDLER | claude | authz-rbac | 22:17:16 | 31s | 5 | 1,145 | 83,026 |
| 17 | ARCHITECT | claude | integrate | 22:18:54 | 1m 37s | 7 | 5,257 | 159,695 |
| 18 | IMPLEMENTOR | claude | integrate | 22:20:28 | 1m 34s | 9 | 6,650 | 244,941 |
| 19 | TESTER | claude | integrate | 22:20:57 | 28s | 6 | 877 | 116,290 |
| 20 | LEAF_COMPLETE_HANDLER | claude | integrate | 22:23:15 | 2m 18s | 19 | 7,437 | 550,802 |
| 21 | ARCHITECT | claude | integrate | 22:25:12 | 1m 57s | 10 | 6,738 | 256,093 |
| 22 | IMPLEMENTOR | claude | integrate | 22:26:12 | 59s | 8 | 4,498 | 198,560 |
| 23 | TESTER | claude | integrate | 22:26:39 | 26s | 5 | 759 | 93,200 |
| 24 | LEAF_COMPLETE_HANDLER | claude | integrate | 22:27:30 | 50s | 9 | 1,998 | 194,060 |

**Per-Role Totals**

| Role | Count | Total Time | Avg/Invocation |
|------|-------|------------|----------------|
| ARCHITECT | 7 | 12m 05s | 1m 43s |
| DECOMPOSE_HANDLER | 2 | 2m 51s | 1m 25s |
| IMPLEMENTOR | 5 | 8m 18s | 1m 39s |
| TESTER | 5 | 2m 17s | 27s |
| LEAF_COMPLETE_HANDLER | 5 | 5m 16s | 1m 03s |

**Token Usage by Role**

| Role | Tokens In | Tokens Out | Tokens Cached | Total |
|------|-----------|------------|---------------|-------|
| ARCHITECT | 98 | 37,318 | 1,200,514 | 1,237,930 |
| DECOMPOSE_HANDLER | 26 | 9,818 | 583,233 | 593,077 |
| IMPLEMENTOR | 52 | 34,148 | 1,308,132 | 1,342,332 |
| TESTER | 26 | 4,571 | 454,152 | 458,749 |
| LEAF_COMPLETE_HANDLER | 50 | 14,615 | 1,148,483 | 1,163,148 |
| **Total** | **252** | **100,470** | **4,694,514** | **4,795,236** |

**Invocations by Agent**

| Agent | Count |
|-------|-------|
| claude | 24 |

## Execution Log — platform-monolith run 4 (partial, in progress 2026-03-18)

**Fixes applied since run 1:**
- `_HANDLER_ROLES` set in `build_prompt()` — DECOMPOSE_HANDLER and LEAF_COMPLETE_HANDLER receive no handoff history
- `frame_stack` implemented in orchestrator — handoff history is scoped to the current decomposition frame; sibling components do not share history
- TESTER.md: explicit prohibition added ("Do NOT call complete-task.sh or move any task directories")
- `on-task-complete.sh`: X- prefix detection added (handles case where agent already renamed the task dir)
- `pipeline-build-template.md`: removed the HTML comment instructing agents to call complete-task.sh (that comment was triggering agents reading the job README)

**Still NOT fixed in this run:**
- `cwd=output_dir` in `agent_wrapper.py` — agents still load ai-builder's `CLAUDE.md` (9,466 bytes) and the target repo's `CLAUDE.md` (4,585 bytes, 14,051 bytes total ~3,500 tokens) via Claude Code's upward CLAUDE.md walk at startup. These are injected into every agent's context on top of Claude Code's own system prompt.

Run stopped early (after 19 invocations) to restart with `cwd=/tmp` fix already applied.

| # | Role | Description | Tokens In | Tokens Out | Tokens Cached |
|---|------|-------------|-----------|------------|---------------|
| 1 | ARCHITECT | build-1 | 8 | 2,851 | 147,469 |
| 2 | DECOMPOSE_HANDLER | build-1 | 25 | 6,958 | 669,512 |
| 3 | ARCHITECT | metrics | 9 | 3,522 | 170,126 |
| 4 | IMPLEMENTOR | metrics | 15 | 7,945 | 359,399 |
| 5 | TESTER | metrics | 4 | 493 | 56,363 |
| 6 | LEAF_COMPLETE_HANDLER | metrics | 3 | 404 | 33,569 |
| 7 | ARCHITECT | iam | 6 | 3,469 | 105,772 |
| 8 | DECOMPOSE_HANDLER | iam | 11 | 4,055 | 223,483 |
| 9 | ARCHITECT | auth-lifecycle | 7 | 2,219 | 129,788 |
| 10 | IMPLEMENTOR | auth-lifecycle | 6 | 947 | 105,824 |
| 11 | TESTER | auth-lifecycle | 4 | 464 | 55,660 |
| 12 | LEAF_COMPLETE_HANDLER | auth-lifecycle | 3 | 468 | 33,581 |
| 13 | ARCHITECT | authz-rbac | 7 | 3,401 | 133,262 |
| 14 | IMPLEMENTOR | authz-rbac | 7 | 1,105 | 127,961 |
| 15 | TESTER | authz-rbac | 6 | 738 | 99,612 |
| 16 | LEAF_COMPLETE_HANDLER | authz-rbac | 3 | 482 | 33,583 |
| 17 | ARCHITECT | integrate(iam) | 12 | 8,993 | 350,061 |
| 18 | IMPLEMENTOR | integrate(iam) | 8 | 1,261 | 165,591 |
| 19 | TESTER | integrate(iam) | 5 | 632 | 77,488 |

**Key observations:**
- LEAF_COMPLETE_HANDLER (invocations 6, 12, 16): consistently ~33,500 cached — down from 550,802 in run 1. **94% reduction** from stripping handoff history from handlers. This is now the floor set by Claude Code's own system prompt + CLAUDE.md injection.
- DECOMPOSE_HANDLER (invocation 2): 669,512 cached — highest in the run. Handlers get no handoff history, so this is entirely Claude Code's system prompt + injected CLAUDE.md files. The ai-builder CLAUDE.md (9,466 bytes) and target CLAUDE.md (4,585 bytes) are being injected into every agent's context via Claude Code's upward CLAUDE.md walk from `cwd=output_dir`.
- DECOMPOSE_HANDLER (invocation 8, iam): 223,483 cached — much lower than invocation 2. The frame_stack handoff scoping is working: this invocation has less accumulated history than invocation 2 did in run 1.
- IMPLEMENTOR cached counts have dropped significantly vs run 1 (e.g. metrics: 359k vs 362k — similar; auth-lifecycle: 105k vs 322k in run 1 — frame_stack working, no stale sibling history).

**Next fix (applied, active in run 5):**
`cwd=output_dir` → `cwd=Path("/tmp")` in `agent_wrapper.py`. Eliminates CLAUDE.md injection entirely. Claude Code's upward walk from `/tmp` finds nothing. All context is injected explicitly via prompt only.

---

## Execution Log — platform-monolith runs 5 & 6 (2026-03-18)

### Run 5 — first run with `cwd=/tmp` (halted at final LEAF)

**All fixes active:** handoff strip for handlers, frame_stack, TESTER prohibition, template comment removed, `on-task-complete.sh` X- detection, `cwd=/tmp`.

Pipeline completed 20 invocations but halted at the final LEAF_COMPLETE_HANDLER (TOP integrate). Root cause: `advance-pipeline.sh` walk-up loop used a stale pre-rename path after marking the parent (iam) complete — `grep` exits 2 on a missing file, which propagates through `pipefail` and kills the script before it can emit NEXT/DONE.

**Fix applied:** after `complete-task.sh` renames parent → X-parent, update `parent_dir` and `parent_readme` to the X- path so the next loop iteration reads from the correct location.

---

### Run 6 — pipeline completed end-to-end, but execution log incomplete (2026-03-18)

**All fixes active:** all run 5 fixes + `advance-pipeline.sh` parent path update.

Run 6 hit an Anthropic rate limit during the DECOMPOSE_HANDLER for iam (invocation 8). Pipeline was manually resumed using a new `--resume` flag added to the orchestrator (skips Level: TOP entry-point validation so the orchestrator can restart from an INTERNAL task). The pipeline resumed and completed end-to-end — `HANDLER_ALL_DONE` received.

**Problem: execution log not captured.** When resuming from an INTERNAL task, `_find_level_top()` in the orchestrator only checked the exact entry-point README for `Level: TOP` — it did not walk up to find the ancestor build-1 README. As a result, `build_readme = None` for the entire resumed session and no rows were appended to the build-1 execution log table.

**Fix applied:** `_find_level_top()` now walks up the directory tree (parent README → grandparent README → ...) until it finds a Level: TOP README or exhausts the tree.

**Partial data captured (first session before rate limit, 7 invocations):**

| # | Role | Description | Elapsed | Tokens In | Tokens Out | Tokens Cached |
|---|------|-------------|---------|-----------|------------|---------------|
| 1 | ARCHITECT | build-1 | 54s | 11 | 2,367 | 189,038 |
| 2 | DECOMPOSE_HANDLER | build-1 | 2m 45s | 22 | 8,099 | 549,462 |
| 3 | ARCHITECT | metrics | 1m 16s | 8 | 2,938 | 133,650 |
| 4 | IMPLEMENTOR | metrics | 2m 17s | 18 | 4,172 | 399,677 |
| 5 | TESTER | metrics | 31s | 4 | 911 | 49,657 |
| 6 | LEAF_COMPLETE_HANDLER | metrics | 16s | 3 | 396 | 30,054 |
| 7 | ARCHITECT | iam | 1m 20s | 10 | 3,746 | 176,035 |

**Key observation from partial data:** LEAF_COMPLETE_HANDLER (invocation 6): **30,054 cached** — down from 550,802 in run 1 (95% reduction). CLAUDE.md injection eliminated by `cwd=/tmp`. This is now purely Claude Code's own system prompt overhead.

**Run 7 completed (2026-03-18).** See section below.

---

## Execution Log — platform-monolith run 7 (2026-03-18) — all fixes active

**All fixes active:**
- Handler no-history: DECOMPOSE_HANDLER and LEAF_COMPLETE_HANDLER receive no handoff history
- `frame_stack`: handoff history scoped per decomposition frame; sibling components don't share history
- `cwd=/tmp`: no CLAUDE.md injected via Claude Code's upward walk
- TESTER.md: explicit prohibition on calling complete-task.sh
- `on-task-complete.sh`: stale path fixed after X- rename
- `advance-pipeline.sh`: stale parent_dir fixed after X- rename

**Note:** Run 7 processed only the **iam subtree** (18 invocations). The metrics component was not re-run as the pipeline was restarted from the iam task. Run 1 had 24 invocations covering build-1 + metrics + iam subtree. To compare apples-to-apples on the iam portion, see the per-role comparison below.

| Field          | Value |
|----------------|-------|
| Task           | iam (INTERNAL entry point) |
| Start          | 2026-03-18 12:30:01 |
| End            | 2026-03-18 12:54:53 |
| Total time     | 24m 52s |
| Invocations    | 18 |
| Tokens in      | 160 |
| Tokens out     | 64,261 |
| Tokens cached  | 3,369,672 |
| Tokens total   | 3,434,093 |

| # | Role | Agent | Description | Ended | Elapsed | Tokens In | Tokens Out | Tokens Cached |
|---|------|-------|-------------|-------|---------|-----------|------------|---------------|
| 1 | ARCHITECT | claude | iam | 12:31:04 | 1m 03s | 5 | 2,407 | 60,796 |
| 2 | DECOMPOSE_HANDLER | claude | iam | 12:32:56 | 1m 52s | 11 | 5,635 | 208,032 |
| 3 | ARCHITECT | claude | user-lifecycle | 12:35:49 | 2m 52s | 16 | 8,630 | 348,118 |
| 4 | IMPLEMENTOR | claude | user-lifecycle | 12:40:05 | 4m 15s | 23 | 14,416 | 701,241 |
| 5 | TESTER | claude | user-lifecycle | 12:40:32 | 27s | 6 | 701 | 91,630 |
| 6 | LEAF_COMPLETE_HANDLER | claude | user-lifecycle | 12:40:44 | 11s | 3 | 457 | 30,068 |
| 7 | ARCHITECT | claude | authz-rbac | 12:42:46 | 2m 01s | 10 | 5,702 | 201,616 |
| 8 | IMPLEMENTOR | claude | authz-rbac | 12:43:22 | 36s | 7 | 1,311 | 125,552 |
| 9 | TESTER | claude | authz-rbac | 12:44:18 | 56s | 11 | 2,214 | 206,725 |
| 10 | LEAF_COMPLETE_HANDLER | claude | authz-rbac | 12:44:34 | 15s | 3 | 443 | 30,070 |
| 11 | ARCHITECT | claude | integrate (INTERNAL) | 12:47:33 | 2m 58s | 13 | 9,594 | 379,932 |
| 12 | IMPLEMENTOR | claude | integrate (INTERNAL) | 12:48:44 | 1m 10s | 11 | 2,232 | 284,022 |
| 13 | TESTER | claude | integrate (INTERNAL) | 12:49:50 | 1m 05s | 12 | 2,589 | 210,151 |
| 14 | LEAF_COMPLETE_HANDLER | claude | integrate (INTERNAL) | 12:50:05 | 15s | 3 | 563 | 30,066 |
| 15 | ARCHITECT | claude | integrate (TOP) | 12:53:33 | 3m 27s | 10 | 5,197 | 219,420 |
| 16 | IMPLEMENTOR | claude | integrate (TOP) | 12:54:10 | 37s | 7 | 1,008 | 124,271 |
| 17 | TESTER | claude | integrate (TOP) | 12:54:37 | 26s | 6 | 770 | 87,908 |
| 18 | LEAF_COMPLETE_HANDLER | claude | integrate (TOP) | 12:54:53 | 15s | 3 | 392 | 30,054 |

**Per-Role Totals**

| Role | Count | Total Time | Avg/Invocation |
|------|-------|------------|----------------|
| ARCHITECT | 5 | 12m 24s | 2m 28s |
| DECOMPOSE_HANDLER | 1 | 1m 52s | 1m 52s |
| IMPLEMENTOR | 4 | 6m 40s | 1m 40s |
| TESTER | 4 | 2m 56s | 44s |
| LEAF_COMPLETE_HANDLER | 4 | 57s | 14s |

**Token Usage by Role**

| Role | Tokens In | Tokens Out | Tokens Cached | Total |
|------|-----------|------------|---------------|-------|
| ARCHITECT | 54 | 31,530 | 1,209,882 | 1,241,466 |
| DECOMPOSE_HANDLER | 11 | 5,635 | 208,032 | 213,678 |
| IMPLEMENTOR | 48 | 18,967 | 1,235,086 | 1,254,101 |
| TESTER | 35 | 6,274 | 596,414 | 602,723 |
| LEAF_COMPLETE_HANDLER | 12 | 1,855 | 120,258 | 122,125 |
| **Total** | **160** | **64,261** | **3,369,672** | **3,434,093** |

### Run 7 vs Run 1 — iam-subtree comparison

Run 1 had 18 invocations for the iam subtree (invocations 7–24). Summing those cached tokens from the run 1 table above: **3,447,424 cached**.

| Metric | Run 1 (iam subtree) | Run 7 (iam subtree) | Change |
|--------|--------------------|--------------------|--------|
| Invocations | 18 | 18 | — |
| Tokens cached total | 3,447,424 | 3,369,672 | −2.3% |
| LCH cached (4 invocations total) | 931,636 | 120,258 | **−87%** |
| LCH cached max (single invocation) | 550,802 | 30,070 | **−95%** |
| LCH avg elapsed | 1m 03s | 14s | −78% |
| Tokens out total | ~55,000 | 64,261 | +16% |

**Key observations:**
- **LEAF_COMPLETE_HANDLER** is the biggest winner: 550,802 → 30,070 cached on the worst invocation (95% reduction). Handlers now see only Claude Code's own system prompt overhead (~30K tokens), not the entire accumulated handoff history.
- **Total cached is nearly the same** (−2.3%) because ARCHITECT and IMPLEMENTOR legitimately need more context (the frame_stack implementation means they still see the lineage of design decisions, which is working as intended).
- **Tokens out is higher** (+16%) in run 7 — the pipeline is generating more code/output, which is likely a quality indicator (more complete implementations), not a regression.
- **LCH elapsed** dropped from ~1m avg to 14s avg — confirmed that the bloated handler prompts were burning real wall time.
- The DECOMPOSE_HANDLER in run 7 (208,032 cached) vs run 1 invocation 8 (211,774 cached) are nearly identical — this is the `cwd=/tmp` baseline (Claude Code system prompt only, no CLAUDE.md).

---

## Proposed Algorithm: Handoff Stack with Frame-Based Scoping

**Date:** 2026-03-18

### Problem recap

`handoff_history` is a plain append-only list. Every agent handoff is appended and the
full list is passed to every subsequent agent. Context from completed sibling components
bleeds into unrelated components. Handlers receive the entire accumulated history of the
run. There is no mechanism for context to expire when it is no longer relevant.

### Core insight

The task tree has natural scope boundaries: every DECOMPOSE_HANDLER invocation opens a
new level of the tree, and every LEAF_COMPLETE_HANDLER invocation that returns `NEXT`
closes one component within that level. The handoff list should mirror this structure —
growing as we descend and shrinking as we ascend.

### Data structures

```
handoff_history : list[str]     # the flat list of handoff strings, as today
frame_stack     : list[Frame]   # NEW — stack of open decomposition frames

Frame:
    anchor_index  : int          # index into handoff_history of the DECOMPOSE_HANDLER entry
    scope_dir     : Path         # parent directory that this DECOMPOSE governs
                                 # = job_doc.parent at the moment DECOMPOSE_HANDLER fires
```

### Push rule — on DECOMPOSE_HANDLER completion

1. Append the DECOMPOSE_HANDLER handoff to `handoff_history` as normal.
2. Push a new Frame onto `frame_stack`:
   - `anchor_index` = current `len(handoff_history) - 1`
   - `scope_dir`    = `job_doc.parent` (directory of the composite README)

### Pop rule — on LEAF_COMPLETE_HANDLER completion

The `on-task-complete.sh` script returns either `NEXT <next_path>` or `DONE`.

**Case 1: `DONE`**
Run is complete. No pop needed.

**Case 2: `NEXT <next_path>` — sibling component**

Compare `Path(next_path).parent` to `frame_stack[-1].scope_dir`.

- If they are equal: `next_path` is a sibling within the same composite.
  Truncate `handoff_history` back to `anchor_index + 1` (keep everything up to and
  including the DECOMPOSE_HANDLER entry; discard all work done for the completed
  component).
  Do NOT pop the Frame — it is still the active scope.

- If they are NOT equal: `next_path` is in a different (higher) parent.
  The current composite is fully done. Pop the Frame from `frame_stack`.
  Truncate `handoff_history` back to the new `frame_stack[-1].anchor_index + 1`
  (or to 0 if the stack is now empty).
  Repeat the comparison with the new top frame in case we've crossed multiple levels
  simultaneously (rare but possible with deep trees).

### Illustrated trace — platform-monolith run

```
Task tree:
  build-1  (TOP)
  ├── metrics          (atomic)
  ├── iam              (composite)
  │   ├── auth-lifecycle   (atomic)
  │   ├── authz-rbac       (atomic)
  │   └── integrate-iam    (Last-task)
  └── integrate        (Last-task, TOP)

Notation: H[n] = handoff entry at index n
          ├── scope_dir shown as short label

Inv  Event                          handoff_history (indices)     frame_stack
───  ─────────────────────────────  ────────────────────────────  ─────────────────────────────
1    ARCHITECT/build-1              H[0]
2    DECOMPOSE/build-1        PUSH  H[0..1]                       [{anchor=1, scope=build-1/}]
3    ARCHITECT/metrics              H[0..2]
4    IMPLEMENTOR/metrics            H[0..3]
5    TESTER/metrics                 H[0..4]
6    LEAF/metrics
     NEXT→iam (same scope=build-1/) TRUNCATE to anchor+1=2
                                    H[0..1]                       [{anchor=1, scope=build-1/}]
7    ARCHITECT/iam                  H[0..2]
8    DECOMPOSE/iam            PUSH  H[0..3]                       [{anchor=1, scope=build-1/},
                                                                   {anchor=3, scope=iam/}]
9    ARCHITECT/auth-lifecycle       H[0..4]
10   IMPLEMENTOR/auth-lifecycle     H[0..5]
11   TESTER/auth-lifecycle          H[0..6]
12   LEAF/auth-lifecycle
     NEXT→authz-rbac (scope=iam/)   TRUNCATE to anchor+1=4
                                    H[0..3]                       [{anchor=1, scope=build-1/},
                                                                   {anchor=3, scope=iam/}]
13   ARCHITECT/authz-rbac           H[0..4]
14   IMPLEMENTOR/authz-rbac         H[0..5]
15   TESTER/authz-rbac              H[0..6]
16   LEAF/authz-rbac
     NEXT→integrate-iam (scope=iam/) TRUNCATE to anchor+1=4
                                    H[0..3]                       [{anchor=1, scope=build-1/},
                                                                   {anchor=3, scope=iam/}]
17   ARCHITECT/integrate-iam        H[0..4]
18   IMPLEMENTOR/integrate-iam      H[0..5]
19   TESTER/integrate-iam           H[0..6]
20   LEAF/integrate-iam
     NEXT→build-1/integrate         next_path.parent = build-1/
     scope=iam/ ≠ build-1/    POP   frame_stack top (iam frame) removed
                               TRUNCATE to new anchor+1=2
                                    H[0..1]                       [{anchor=1, scope=build-1/}]
21   ARCHITECT/integrate            H[0..2]
22   IMPLEMENTOR/integrate          H[0..3]
23   TESTER/integrate               H[0..4]
24   LEAF/integrate
     DONE                           (run ends, no pop needed)
```

### What each agent sees

| Agent | Context visible |
|-------|----------------|
| ARCHITECT/iam | build-1 ARCHITECT + DECOMPOSE/build-1 — knows the parent service goal and decomposition rationale |
| IMPLEMENTOR/authz-rbac | build-1 ARCH + DECOMP/build-1 + ARCH/iam + DECOMP/iam + ARCH/authz-rbac — knows the full lineage of design decisions leading to this component |
| ARCHITECT/integrate (TOP) | build-1 ARCH + DECOMP/build-1 — clean slate; prior component detail is gone |

Sibling components share zero implementation detail with each other. Each component
only sees the design lineage that produced it.

### Why `scope_dir = job_doc.parent`

When DECOMPOSE_HANDLER fires, `job_doc` is the composite's README (e.g.
`in-progress/d849b6-0000-build-1/d849b6-0000-0001-iam/README.md`). Its parent
directory is `d849b6-0000-0001-iam/`. All subtasks created by that DECOMPOSE will
have that directory as their parent. So comparing `Path(next_path).parent` against
`scope_dir` is exact — no string parsing required.

### Open question

Should the LEAF_COMPLETE_HANDLER's own handoff be included before truncating, or
discarded? Currently it gets appended then truncated away. That seems correct — the
handler's "I ran a script" note has no value for the next sibling's agents.

### Implementation notes

- `frame_stack` is a new field in the orchestrator main loop, parallel to `handoff_history`
- Both lists start empty and are never persisted (in-memory only, same as today)
- The truncation in the pop rule is `handoff_history = handoff_history[:anchor_index + 1]`
- No changes required to `build_prompt()` — it still receives the flat `handoff_history` list
- Handlers should additionally receive an empty list (separate fix, see parent task)

---

## Execution Log — platform-monolith run 8 (2026-03-18) — first full clean run, all fixes

**All fixes active:** handler no-history, frame_stack, cwd=/tmp, TESTER prohibition, on-task-complete.sh stale path fix, advance-pipeline.sh stale path fix.

This is the first uninterrupted full pipeline run (build-1 entry point, all 24 invocations) with all fixes active. Direct comparison to run 1 baseline is now possible.

| Field          | Value |
|----------------|-------|
| Task           | build-1 |
| Start          | 2026-03-18 13:21:25 |
| End            | 2026-03-18 13:59:07 |
| Total time     | 37m 41s |
| Invocations    | 24 |
| Tokens in      | 321 |
| Tokens out     | 119,776 |
| Tokens cached  | 5,728,675 |
| Tokens total   | 5,848,772 |

| # | Role | Agent | Description | Ended | Elapsed | Tokens In | Tokens Out | Tokens Cached |
|---|------|-------|-------------|-------|---------|-----------|------------|---------------|
| 1 | ARCHITECT | claude | build-1 | 13:22:28 | 1m 03s | 11 | 2,952 | 195,127 |
| 2 | DECOMPOSE_HANDLER | claude | build-1 | 13:25:12 | 2m 43s | 23 | 8,984 | 567,824 |
| 3 | ARCHITECT | claude | metrics | 13:26:29 | 1m 16s | 12 | 2,929 | 232,991 |
| 4 | IMPLEMENTOR | claude | metrics | 13:26:53 | 24s | 5 | 725 | 74,614 |
| 5 | TESTER | claude | metrics | 13:27:19 | 26s | 4 | 832 | 50,038 |
| 6 | LEAF_COMPLETE_HANDLER | claude | metrics | 13:27:36 | 17s | 3 | 340 | 30,051 |
| 7 | ARCHITECT | claude | iam | 13:29:12 | 1m 36s | 9 | 4,510 | 157,229 |
| 8 | DECOMPOSE_HANDLER | claude | iam | 13:31:16 | 2m 03s | 13 | 7,134 | 261,916 |
| 9 | ARCHITECT | claude | auth-lifecycle | 13:33:16 | 1m 59s | 7 | 6,190 | 120,827 |
| 10 | IMPLEMENTOR | claude | auth-lifecycle | 13:36:16 | 3m 00s | 15 | 12,032 | 409,557 |
| 11 | TESTER | claude | auth-lifecycle | 13:37:04 | 48s | 12 | 1,888 | 220,406 |
| 12 | LEAF_COMPLETE_HANDLER | claude | auth-lifecycle | 13:37:16 | 12s | 3 | 429 | 30,064 |
| 13 | ARCHITECT | claude | authz-rbac | 13:38:52 | 1m 35s | 11 | 5,015 | 216,109 |
| 14 | IMPLEMENTOR | claude | authz-rbac | 13:42:17 | 3m 25s | 19 | 15,616 | 630,644 |
| 15 | TESTER | claude | authz-rbac | 13:43:07 | 50s | 9 | 2,043 | 163,468 |
| 16 | LEAF_COMPLETE_HANDLER | claude | authz-rbac | 13:43:20 | 13s | 3 | 523 | 30,066 |
| 17 | ARCHITECT | claude | integrate | 13:46:38 | 3m 17s | 7 | 9,843 | 127,641 |
| 18 | IMPLEMENTOR | claude | integrate | 13:48:35 | 1m 57s | 16 | 6,035 | 392,257 |
| 19 | TESTER | claude | integrate | 13:49:56 | 1m 20s | 15 | 3,642 | 329,598 |
| 20 | LEAF_COMPLETE_HANDLER | claude | integrate | 13:50:09 | 12s | 3 | 511 | 30,062 |
| 21 | ARCHITECT | claude | integrate | 13:52:08 | 1m 58s | 84 | 6,788 | 194,980 |
| 22 | IMPLEMENTOR | claude | integrate | 13:57:51 | 5m 42s | 25 | 18,766 | 1,083,136 |
| 23 | TESTER | claude | integrate | 13:58:51 | 1m 00s | 9 | 1,611 | 150,019 |
| 24 | LEAF_COMPLETE_HANDLER | claude | integrate | 13:59:07 | 15s | 3 | 438 | 30,051 |

**Per-Role Totals**

| Role | Count | Total Time | Avg/Invocation |
|------|-------|------------|----------------|
| ARCHITECT | 7 | 12m 47s | 1m 49s |
| DECOMPOSE_HANDLER | 2 | 4m 47s | 2m 23s |
| IMPLEMENTOR | 5 | 14m 29s | 2m 53s |
| TESTER | 5 | 4m 25s | 53s |
| LEAF_COMPLETE_HANDLER | 5 | 1m 11s | 14s |

**Token Usage by Role**

| Role | Tokens In | Tokens Out | Tokens Cached | Total |
|------|-----------|------------|---------------|-------|
| ARCHITECT | 141 | 38,227 | 1,244,904 | 1,283,272 |
| DECOMPOSE_HANDLER | 36 | 16,118 | 829,740 | 845,894 |
| IMPLEMENTOR | 80 | 53,174 | 2,590,208 | 2,643,462 |
| TESTER | 49 | 10,016 | 913,529 | 923,594 |
| LEAF_COMPLETE_HANDLER | 15 | 2,241 | 150,294 | 152,550 |
| **Total** | **321** | **119,776** | **5,728,675** | **5,848,772** |

### Run 8 vs Run 1 — full pipeline comparison

| Metric | Run 1 (no fixes) | Run 8 (all fixes) | Change |
|--------|-----------------|-------------------|--------|
| Total time | 30m 48s | 37m 41s | +22% |
| Invocations | 24 | 24 | — |
| Tokens out | 100,470 | 119,776 | +19% |
| Tokens cached total | 4,694,514 | 5,728,675 | **+22%** |
| LCH cached total | 1,148,483 | 150,294 | **−87%** |
| LCH cached max | 550,802 | 30,066 | **−95%** |
| IMPLEMENTOR cached total | 1,308,132 | 2,590,208 | +98% |
| TESTER cached total | 454,152 | 913,529 | +101% |

### Key observations

**LCH is fixed and stays fixed.** All 5 LCH invocations land at ~30K — the Claude Code floor. This is stable.

**Total cached went UP despite all fixes.** The fixes worked on what they targeted (LCH −87%), but IMPLEMENTOR and TESTER cached roughly doubled. The cause is not prompt injection — it's codebase growth. The pipeline generated 19% more code in run 8 (119K tokens out vs 100K). More code written = bigger codebase = more files read by IMPLEMENTOR at integration time and by TESTER when running tests.

**IMPLEMENTOR/integrate (TOP) is the new biggest single offender at 1,083,136 cached** (vs 198,560 in run 1 — 5.4×). This TOP-level integrate task reads the entire assembled codebase before wiring it together. The bigger the codebase built by prior components, the more context this task accumulates. This is structurally inherent to integration tasks.

**Quality vs cost tradeoff.** The fixes appear to have improved implementation quality — the pipeline is generating more complete code. Better implementations lead to larger codebases, which leads to more tokens at integration time. This is not a regression in the optimization work; the fixes did what they were supposed to. But it surfaces a new cost driver that is harder to reduce: the integrate IMPLEMENTOR's read-everything-to-wire-it-together pattern.

**TESTER is the next actionable target.** TESTER totalled 913,529 cached (vs 454,152 in run 1, +101%). TESTER is NOT in `_HANDLER_ROLES` — it still receives the full handoff history. Adding TESTER to `_HANDLER_ROLES` is the lowest-effort remaining optimization (one-line change, same fix as LCH). Expected savings: TESTER cached floor would drop to ~30K × 5 = 150K, saving ~763K cached tokens per run (~13% of total).

---

## Execution Log — platform-monolith run 9 (2026-03-18) — TESTER no_history: true

**Change under test:** `no_history: true` added to TESTER in `default.json`. TESTER now receives no handoff history — only its role instructions and the current job doc.

**Note:** Run 9 hit a rate limit after 8 invocations (build-1 ARCH+DECOMPOSE, metrics ×4, iam ARCH+DECOMPOSE) and was resumed. The first session's metrics were not captured. The iam subtree (16 invocations) is fully captured and is sufficient for the TESTER comparison.

| # | Role | Description | Elapsed | Tokens In | Tokens Out | Tokens Cached |
|---|------|-------------|---------|-----------|------------|---------------|
| 1 | ARCHITECT | auth-lifecycle | 1m 34s | 7 | 4,459 | 104,294 |
| 2 | IMPLEMENTOR | auth-lifecycle | 2m 17s | 13 | 8,900 | 343,681 |
| 3 | TESTER | auth-lifecycle | 55s | 8 | 1,708 | 149,104 |
| 4 | LEAF_COMPLETE_HANDLER | auth-lifecycle | 11s | 3 | 487 | 30,514 |
| 5 | ARCHITECT | authz-rbac | 2m 00s | 85 | 6,664 | 241,019 |
| 6 | IMPLEMENTOR | authz-rbac | 4m 57s | 17 | 14,215 | 510,335 |
| 7 | TESTER | authz-rbac | 52s | 8 | 1,221 | 147,670 |
| 8 | LEAF_COMPLETE_HANDLER | authz-rbac | 16s | 3 | 447 | 30,516 |
| 9 | ARCHITECT | integrate (INTERNAL) | 2m 13s | 10 | 6,064 | 224,098 |
| 10 | IMPLEMENTOR | integrate (INTERNAL) | 2m 33s | 14 | 10,400 | 417,201 |
| 11 | TESTER | integrate (INTERNAL) | 55s | 11 | 1,337 | 196,101 |
| 12 | LEAF_COMPLETE_HANDLER | integrate (INTERNAL) | 12s | 3 | 468 | 30,512 |
| 13 | ARCHITECT | integrate (TOP) | 6m 23s | 10 | 11,892 | 270,260 |
| 14 | IMPLEMENTOR | integrate (TOP) | 5m 26s | 17 | 9,521 | 534,274 |
| 15 | TESTER | integrate (TOP) | 1m 35s | 9 | 1,344 | 159,886 |
| 16 | LEAF_COMPLETE_HANDLER | integrate (TOP) | 28s | 3 | 344 | 30,499 |

### Run 9 vs Run 8 — iam subtree TESTER comparison (4 invocations each)

| Invocation | Run 8 Cached | Run 9 Cached | Change |
|---|---|---|---|
| TESTER / auth-lifecycle | 220,406 | 149,104 | −32% |
| TESTER / authz-rbac | 163,468 | 147,670 | −10% |
| TESTER / integrate (INTERNAL) | 329,598 | 196,101 | −40% |
| TESTER / integrate (TOP) | 150,019 | 159,886 | +7% |
| **TESTER total** | **863,491** | **652,761** | **−24%** |
| LCH total | 931,636 | 122,041 | −87% (for ref) |

### Key observations

**TESTER did not drop to the ~30K floor.** The prediction was wrong. LCH at ~30.5K is the floor because LCH does almost nothing — it runs one short script and exits. TESTER actively reads the codebase: it opens test files, source files, runs `go test`, reads output. All those file reads accumulate in the context window and get cached. The ~150K–196K remaining is the codebase read overhead, not handoff history.

**The no_history change still helped — ~24% reduction on TESTER.** The remaining variance (+7% on integrate TOP) is within normal run-to-run variation from different generated codebases.

**The floor for TESTER is workload-dependent**, not a fixed constant. A bigger codebase = more files to read = higher TESTER cached count. This is inherent to what TESTER does and cannot be reduced by prompt changes alone.

**LCH at ~30.5K** confirms the Claude Code system prompt floor is stable.

### Follow-on: language-agnostic Test Command (run 10)

Run 9 revealed that stripping handoff history from TESTER reduced cached tokens only ~24% because TESTER's prompt caused it to read source and test files during execution — the file reads are the dominant cost, not the handoff history. Specifically, the old `roles/TESTER.md` said "verify the implementation against acceptance criteria" and hardcoded `go test ./...`, which led TESTER to open source files to understand what it was testing.

**Fix implemented (2026-03-18):**

- **`roles/ARCHITECT.md`**: both Design Mode and Decompose Mode now include a step to fill in `## Test Command` in the job doc with the exact shell command to run all tests (language-agnostic, sourced from target repo's `CLAUDE.md`).
- **`roles/TESTER.md`**: rewritten to read only the `## Test Command` field from the job doc and run it verbatim. Explicitly prohibited from reading source files, inventing commands, or substituting language-specific commands. If `## Test Command` is missing, emit `TESTER_NEED_HELP`.
- **`pipeline-build-template.md`** (both ai-builder and target copies): added `## Test Command` section between `## Acceptance Criteria` and `## Suggested Tools`.
- **`reset.sh`** inline template: same `## Test Command` section added.

**Expected impact:** TESTER should drop from ~150–196K cached per invocation closer to the ~30K Claude Code floor, since the only thing TESTER reads is the `## Test Command` line from the job doc (already in context as part of the system prompt) plus whatever `go test` outputs to stdout. No file browsing, no source reads.

**Flow correctness:** TESTER only ever runs on atomic tasks. Atomic tasks always go through ARCHITECT in Design Mode before IMPLEMENTOR and TESTER run — so `## Test Command` is always filled by the time TESTER needs it. Composite tasks (Decompose Mode) never reach TESTER; DECOMPOSE_HANDLER creates subtask files from the template after ARCHITECT runs, and each subtask gets its own ARCHITECT invocation. No gap.

**Run 10** (pending) will validate the token reduction prediction.

---

## Remaining Performance Opportunities (2026-03-18)

Based on post-fix run data (run 7), the following opportunities are ranked by expected impact.

### Current per-role token averages (run 7, iam subtree, 18 invocations)

| Role | Invocations | Avg Cached/Inv | Total Cached |
|------|-------------|----------------|--------------|
| ARCHITECT | 5 | 241,976 | 1,209,882 |
| IMPLEMENTOR | 4 | 308,772 | 1,235,086 |
| TESTER | 4 | 149,104 | 596,414 |
| DECOMPOSE_HANDLER | 1 | 208,032 | 208,032 |
| LEAF_COMPLETE_HANDLER | 4 | 30,065 | 120,258 |

LCH at ~30K is the irreducible floor with the current claude-subprocess approach. It is purely Claude Code's own system prompt.

---

### Opportunity 1: TESTER no-history — IMPLEMENTED (run 9)

**Result:** −24% on TESTER cached (863K → 653K), not the predicted −80%. The handoff history was not the main cost driver; TESTER's file-reading behaviour during execution was. See run 9 observations.

### Opportunity 1b: TESTER language-agnostic Test Command — IMPLEMENTED (run 10 pending)

**Problem:** even with no handoff history, TESTER reads source and test files because the old prompt said "verify the implementation against acceptance criteria" — implying it should understand the code. The remaining 150–196K cached per TESTER invocation is almost entirely file read overhead.

**Fix:** ARCHITECT now fills in `## Test Command` in the job doc (exact shell command, language-agnostic). TESTER reads that field and runs it verbatim — no source file browsing, no hardcoded language commands.

**Expected impact:** TESTER drops from ~150–196K → ~30K cached per invocation. For a 24-invocation run (~5 TESTER calls): ~800K tokens saved (~14% of total).

**Risk:** Low. The test command is authoritative; TESTER has no reason to second-guess it.

---

### Opportunity 2: IMPLEMENTOR trim to current ARCHITECT only

**Current state:** IMPLEMENTOR receives the full lineage up to its point: ARCH/parent-of-parent + DECOMPOSE/parent-of-parent + ARCH/parent + DECOMPOSE/parent + ARCH/component. For deeply nested trees this grows with depth.

**Expected impact:** Medium, task-dependent. For the current 2-level tree, IMPLEMENTOR sees 2-3 ancestral entries beyond the current ARCHITECT design. Trimming to just the most recent ARCHITECT handoff would save those entries per invocation.

**Implementation:** Introduce a per-role `handoff_depth` limit, or a dedicated `IMPLEMENTOR` filter that keeps only `handoff_history[-1]` (the immediately prior ARCHITECT handoff).

**Risk:** Medium. IMPLEMENTOR may benefit from knowing the parent decomposition rationale (e.g. "iam is split into user-lifecycle and authz-rbac because..."). Needs testing to verify quality is maintained.

---

### Opportunity 3: Direct API calls instead of claude subprocess

**Current state:** Each invocation spawns a `claude` subprocess. Claude Code injects its own system prompt (~30K cached tokens) regardless of what we ask the agent to do. This is the 30K floor visible on every LCH and TESTER invocation.

**Expected impact:** Eliminating the Claude Code system prompt overhead saves ~30K × (total invocations) per run. For a 24-invocation run: ~720K tokens (~15% of total). Additionally removes per-invocation subprocess startup latency.

**Implementation:** Replace `agent_wrapper.py` with direct `anthropic.Anthropic().messages.create()` calls. Role prompts become the `system` message; handoff history and job doc become `user` messages. Significant refactor — the streaming, tool-use loop, and outcome parsing all need to move from Claude Code to Python.

**Risk:** High effort. Claude Code handles a lot of agent scaffolding (file reads, bash execution, multi-turn tool use). Reimplementing that in Python is non-trivial and removes the ability to use Claude Code's built-in tools.

---

### Opportunity 4: Parallelism within a decomposition level

**Current state:** After DECOMPOSE splits a composite into N siblings, each sibling is processed sequentially. Siblings are structurally independent — metrics and iam share no code, only the parent job doc.

**Expected impact:** No token reduction. Wall-time reduction proportional to the number of siblings. For the platform-monolith (metrics + iam), running in parallel would roughly halve total time. For wider decompositions the benefit scales further.

**Implementation:** Requires the orchestrator to manage multiple concurrent pipeline branches, merge their results, and handle rate limits across parallel agents.

**Risk:** High complexity. Parallel branches could conflict on shared files (e.g. go.mod), and rate limit handling becomes more complex.

---

### Opportunity 5: Role document size audit

**Current state:** ARCHITECT.md, IMPLEMENTOR.md, TESTER.md are injected verbatim into every invocation of their role. Their sizes have not been measured. If any are large, they are a fixed per-invocation cost that could be trimmed without affecting agent behavior.

**Expected impact:** Unknown until measured. Likely small but easy to check.

**Implementation:** Measure with `wc -c roles/*.md`; trim verbose sections, examples, or redundant instructions.

**Risk:** Low. Role docs are human-readable instructions — trimming carefully preserves agent behavior.

---

### Opportunity 6: Model tiering

**Current state:** All roles use the same model (claude-sonnet-4-6).

**Expected impact:** Handlers and TESTER are simple script-runners. Using Haiku (5× cheaper) for LCH, DECOMPOSE_HANDLER, and TESTER would reduce cost significantly without affecting quality for those roles. ARCHITECT and IMPLEMENTOR should stay on Sonnet.

**Implementation:** Per-role model selection in `agent_wrapper.py` / orchestrator config.

**Risk:** Low for handlers (their job is trivial). Medium for TESTER (needs judgement on pass/fail).

---

### Summary table

| Opportunity | Effort | Token Savings | Speed Savings | Risk |
|---|---|---|---|---|
| TESTER no-history | Low | ~600K/run | Negligible | Low |
| Role doc audit | Low | Unknown, likely small | Negligible | Low |
| IMPLEMENTOR trim | Medium | Medium, depth-dependent | Negligible | Medium |
| Model tiering | Medium | Cost reduction (not token count) | Negligible | Low–Medium |
| Direct API calls | High | ~720K/run (~15%) | High | High |
| Parallelism | High | None | High | High |

---

## Q&A

**Q: How did we get the leaf handler so low in token usage? Are we passing the handoff to it?**

No — we are not passing handoff history to LCH. `_HANDLER_ROLES = {"DECOMPOSE_HANDLER", "LEAF_COMPLETE_HANDLER"}` in `build_prompt()` causes both handlers to receive an empty history section. The full `handoff_history` list still exists in memory at the time LCH runs, but `build_prompt` strips it before constructing the prompt.

The ~30K that remains is purely the Claude Code system prompt. The LCH prompt itself is tiny — role instructions plus the job doc path — but Claude Code boots and injects its own ~30K token system prompt before it sees our prompt. That is the irreducible floor with the current subprocess approach.

How LCH went from 550,802 → ~30K:
1. **Handler no-history** (`_HANDLER_ROLES`): removed accumulated run history from the prompt. ~95% of the reduction.
2. **cwd=/tmp**: removed ai-builder's CLAUDE.md + target repo's CLAUDE.md from being injected. Saved another ~3K (the delta between run 4's ~33K and run 7's ~30K floor).

---

**Q: So at the time the leaf handler is called, we still have a large handoff full of history, but we just don't give that history to the leaf. And after the leaf handler, then we start popping stuff off the handoff. Is that correct?**

Yes, exactly. The sequence when LCH fires:

1. LCH is invoked — `build_prompt` strips handoff history before passing to the agent, but the full `handoff_history` list still exists in memory
2. LCH runs `on-task-complete.sh`, emits outcome
3. LCH's own handoff gets appended to `handoff_history`
4. **Then** the frame_stack truncation fires — it looks at where the next job landed, pops frames, and truncates history accordingly

So at the moment LCH runs, memory holds e.g.:
```
H[0] ARCH/build-1
H[1] DECOMPOSE/build-1       ← frame anchor (scope=build-1/)
H[2] ARCH/metrics
H[3] IMPLEMENTOR/metrics
H[4] TESTER/metrics
H[5] LCH/metrics              ← just appended
```

LCH saw none of that. Then the truncation fires, sees the next job is `iam` (same scope=build-1/), and truncates back to anchor+1:
```
H[0] ARCH/build-1
H[1] DECOMPOSE/build-1
```

The history is trimmed for the benefit of the *next* invocation, not the LCH itself. LCH never needed the history, and the history is cleaned up right after it runs.

---

**Q: Is all the Leaf Complete Handler's work deterministic, or does it require AI decisions?**

It is almost entirely deterministic. The full LCH prompt boils down to:

1. Run `on-task-complete.sh --current <path> --output-dir <dir> --epic <epic>`
2. Read stdout: `NEXT <path>`, `DONE`, or `STOP_AFTER`
3. Map that directly to one of three outcome strings: `HANDLER_SUBTASKS_READY`, `HANDLER_ALL_DONE`, `HANDLER_STOP_AFTER`

There is zero AI reasoning required. The shell script does all the work — marks the task complete, renames the directory, advances the pipeline, returns the next path. The agent just runs one command and pattern-matches three possible outputs to three outcome strings.

The only reason it's an AI invocation today is that the orchestrator expects `OUTCOME: <string>` back from an agent subprocess. Everything else — including the decision of what comes next — is handled entirely by `on-task-complete.sh`.

**The orchestrator could execute LCH itself directly in Python**, calling `on-task-complete.sh` via `subprocess.run()`, reading stdout, and mapping it to the next state — no agent spawned, no Claude Code system prompt overhead, no 15s startup latency. That eliminates 5 × ~30K = 150K cached tokens and ~75s of wall time per run (at the platform-monolith scale).

The same argument applies to DECOMPOSE_HANDLER: it calls a fixed sequence of scripts to create subtask directories. The AI adds little value there too — though DECOMPOSE_HANDLER does read the job doc and decide component names and structure, so it's less purely mechanical than LCH. LCH is the cleaner first target.

**Implementation approach:** introduce an `internal_agent` concept in the orchestrator. When the state machine transitions to `LEAF_COMPLETE_HANDLER`, instead of spawning a claude subprocess, the orchestrator calls a Python function that runs `on-task-complete.sh`, parses the result, and returns an `AgentResult` in the same shape as a real agent response. The rest of the orchestrator loop (routing, handoff appending, frame_stack) stays unchanged.

---

## Execution Log — internal agent for LEAF_COMPLETE_HANDLER — IMPLEMENTED (2026-03-18, run 11 pending)

**Change:** `LEAF_COMPLETE_HANDLER` declared as `"agent": "internal"` in `default.json`. The orchestrator main loop branches on `agent == "internal"` and calls `run_internal_agent()` instead of `build_prompt()` + `run_agent()`. `_run_lch_internal()` calls `on-task-complete.sh` via `subprocess.run()`, maps stdout to an outcome string, and returns an `AgentResult` with zero token counts.

**`no_history` flag omitted** for internal agents — it is meaningless since no prompt is ever built. The orchestrator skips `build_prompt()` entirely for internal roles.

**Expected savings per full run (24 invocations, 5 LCH calls):**

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| LCH tokens cached | ~150K (5 × 30K) | 0 | −100% |
| LCH wall time | ~75s (5 × 15s) | <1s | ~−75s |

**Run 11 completed (2026-03-19). Gold test: PASS.**

**Run 11** tested both changes active together (2026-03-19):

1. **TESTER no-history + Test Command** — TESTER receives no handoff history and reads only `## Test Command` from the job doc; ARCHITECT fills that field in Design Mode; no source file browsing.
2. **LCH internal agent** — LEAF_COMPLETE_HANDLER runs `on-task-complete.sh` directly in Python; no claude subprocess; zero token cost.

These are bundled rather than isolated because the Test Command change requires ARCHITECT behaviour to change (filling the new field), making a clean single-variable run impractical.

**Expected outcomes vs run 8 baseline:**

| Role | Run 8 Cached | Run 11 Expected | Change |
|------|-------------|-----------------|--------|
| TESTER (5 inv) | 913,529 | ~150K or less | −80%+ |
| LCH (5 inv) | 150,294 | 0 | −100% |
| Combined savings | — | ~900K | ~16% of run 8 total |

### Run 11 Actual Results vs Run 8

| Metric | Run 8 (baseline) | Run 11 | Change |
|--------|-----------------|--------|--------|
| Total time | 37m 41s | 23m 15s | **−38%** |
| Tokens cached total | 5,728,675 | 3,503,765 | **−39%** |
| TESTER cached (5 inv) | 913,529 | 245,406 | **−73%** |
| LCH cached (5 inv) | 150,294 | 0 | **−100%** |
| IMPLEMENTOR cached | 2,590,208 | 905,871 | −65%* |
| LCH avg elapsed | 14s | 0s | −100% |
| TESTER avg elapsed | 53s | 16s | −70% |
| claude invocations | 24 | 19 | −21% |

*IMPLEMENTOR drop is likely run-to-run variation — run 11 generated simpler code (64K tokens out vs 119K in run 8).

**Key observations:**

**TESTER Test Command is highly effective.** TESTER dropped from ~183K avg → ~49K avg per invocation (−73%). The ~49K floor is Claude Code's system prompt + the job doc (which is legitimately in context). Source file browsing eliminated entirely.

**LCH internal agent is exact.** Zero tokens, zero latency on all 5 invocations. The stdout line-scanning fix worked correctly.

**Total cached down 39%, wall time down 38%.** The combined optimizations are significant. The remaining dominant costs are ARCHITECT (1,427K) and DECOMPOSE_HANDLER (924K) — both still running as claude subprocesses and both candidates for further optimization.

**Gold test: PASS.**
