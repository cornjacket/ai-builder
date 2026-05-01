# Status Reports

Periodic status reports — each one a **delta document** covering the
period since the previous report. Not daily, not session-bound. Cadence
is operator-driven (weekly, twice-weekly, daily — whatever fits), the
way a real staff status meeting works.

Read the most recent report at the start of a new session to understand
where things left off.

When the operator says **"write a status report"** (or natural variants:
"status report", "draft a status report", "write status", "write up the
period"), the AI writes a new `YYYY-MM-DD.md` covering the period since
the previous report. The filename's date is the as-of date.

**Sections:**

- **Work Completed** — narrative summary of what shipped during the
  period. *Not* a 1:1 restatement of `log.md`; that is the atomic
  per-task ground truth. The status report synthesizes log entries into
  themes, outcomes, and decisions.
- **Work In Progress** — what is currently open and where it stands.
- **Next Up** — what comes after the in-progress work, and why.
- **Key Decisions** — non-obvious decisions made during the period
  worth carrying forward.

**Roles:** `log.md` (repo root) is atomic, hash-indexed, per-task
history. Status reports are the human narrative layered on top of it.

**Worktrees:** status reports are produced from `main/` only — they are
a coordination artifact, not per-worktree state.

---

## Log

| Date | Summary |
|------|---------|
| [2026-04-05](2026-04-05.md) | Established recordings for all four full-pipeline regressions; fixed doc reset.sh cp bug; added check-recordings-status.sh; PR #3 open and clean |
| [2026-03-18](2026-03-18.md) | Token optimization: handler no-history, frame_stack, cwd=/tmp, TESTER no-history, Test Command, LCH internal agent; run 8+9 baselines recorded; run 11 pending |
| [2026-03-17](2026-03-17.md) | Split TASK_MANAGER into DECOMPOSE_HANDLER/LEAF_COMPLETE_HANDLER; added --state-machine/--start-state flags; all three regression tests fixed and passing; platform-monolith build metrics recorded |
| [2026-03-16](2026-03-16.md) | Completed tm-tree-traversal (advance-pipeline, on-task-complete, Level field, TM prompt fixes); platform-monolith regression test scaffolded and run twice; ARCHITECT.md contract propagation fix; regression test SOP written |
| [2026-03-14](2026-03-14.md) | Closed f7a6af (three task types, typed scripts); closed d9c12f (orchestrator review); regression test clean; 0838a5-tm-tree-traversal created |
| [2026-03-13](2026-03-13.md) | Decomposition regression test complete (user-service, 8 gold tests pass); 4 orchestrator bugs fixed; design decisions: task README = job doc, main not a component, Oracle contract for current-job.txt |
| [2026-03-11](2026-03-11.md) | Completed 6fdb3a (role extraction, agent_wrapper fixes); multi-level decomposition and DOCUMENTER design brainstorm |
| [2026-03-10](2026-03-10.md) | verify-setup.sh refactor; CLAUDE.md hierarchy and agent operation design discussions; MCP integration task created |
| [2026-03-09](2026-03-09.md) | Completed 651a51-add-project-management-system-template: target/ skeleton, PM role, orchestrator PM mode, regression tests |
