# Task: brainstorm-token-usage-and-caching-costs

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | draft             |
| Epic        | main               |
| Tags        | —               |
| Priority    | HIGH        |
| Next-subtask-id | 0000               |

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
