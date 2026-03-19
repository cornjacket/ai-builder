# Learning: AI Subagent Token Optimization

**Context:** ai-builder runs a multi-role pipeline where each role is a
separate AI agent (Claude Code subprocess). These findings come from
instrumenting the platform-monolith regression across runs 1–11 (2026-03-17
to 2026-03-19).

---

## 1. Handoff history is the biggest lever — but only strip it from roles that don't need it

The orchestrator accumulated all prior agent handoffs into a flat list and
passed it to every subsequent agent. This made sense for design roles
(ARCHITECT needs to know the decomposition rationale) but was pure overhead
for handler roles that just run shell scripts.

Stripping handoff history from LEAF_COMPLETE_HANDLER dropped its cached
tokens from 550K → 30K per invocation (−95%). The fix was trivial: a
per-role `no_history` flag in the state machine JSON.

**Rule:** before passing history to an agent, ask "does this role's reasoning
depend on what prior agents said?" If no, strip it.

---

## 2. There is an irreducible floor per subprocess — Claude Code's own system prompt (~30K tokens)

Every `claude` subprocess injects its own system prompt into the context
regardless of what you ask it to do. This is ~30K cached tokens of unavoidable
overhead per invocation with the subprocess model.

This floor showed up on every handler invocation after handoff history was
stripped — the handler prompt was tiny but the cached count never dropped
below ~30K.

**Implication:** for roles that run many times per pipeline, the per-invocation
system prompt overhead accumulates. A 24-invocation run with 5 handler calls
pays 5 × 30K = 150K tokens in system prompt overhead alone.

---

## 3. Deterministic roles don't need AI at all — replace them with direct Python calls

LEAF_COMPLETE_HANDLER runs one shell script (`on-task-complete.sh`), reads
its output (`NEXT <path>`, `DONE`, or `STOP_AFTER`), and maps it to an
outcome string. There is zero AI reasoning in this loop.

Replacing the claude subprocess with a direct `subprocess.run()` call in
Python eliminates:
- The ~30K cached token system prompt overhead entirely
- ~15s startup latency per invocation
- All token cost (internal agents return zero token counts)

**Rule:** ask "does this role require AI judgement, or is it just running a
script and pattern-matching the output?" If the latter, implement it as an
internal Python function.

**Practical note:** when parsing script output, scan line by line — scripts
often emit status messages before the terminal token, so `startswith()` on
the full stdout blob will fail.

---

## 4. cwd affects what context the agent sees — Claude Code walks up for CLAUDE.md

Claude Code performs an upward directory walk from `cwd` at startup to
discover and inject `CLAUDE.md` files. Running agents with `cwd=output_dir`
caused it to find and inject ai-builder's own `CLAUDE.md` and the target
repo's `CLAUDE.md` (~3,500 tokens) into every agent's context — content that
was irrelevant to the agent's task.

Fix: set `cwd=/tmp`. The upward walk finds nothing; all context is injected
explicitly via the prompt only.

**Rule:** always set `cwd` to a neutral directory (e.g. `/tmp`) for agent
subprocesses unless you specifically want CLAUDE.md injection.

---

## 5. An agent's token cost is driven by what it *reads*, not just what it receives in its prompt

Prediction: stripping handoff history from TESTER would drop it to the ~30K
floor. Actual result: −24% (863K → 653K). The remaining ~650K was not from
the prompt — it was from TESTER reading source and test files during execution.

The prompt said "verify the implementation against acceptance criteria," which
caused TESTER to browse the codebase to understand what it was testing. File
reads accumulate in the context window and get cached just like prompt content.

**Rule:** optimising the prompt is necessary but not sufficient. Also audit
what the agent *does* — file reads, tool calls, and bash output all add to
cached tokens.

---

## 6. Move authoritative information into the job document — don't hardcode it in role prompts

TESTER.md hardcoded `go test ./...` as the test command. This was wrong for
two reasons: it was language-specific, and it gave TESTER no choice but to
read the codebase to understand what it was testing.

Fix: ARCHITECT fills in a `## Test Command` field in the job doc with the
exact command for the target language and repo. TESTER reads that field and
runs it verbatim — no source file browsing, no language assumptions.

**General principle:** role prompts should describe *behaviour*; job documents
should carry *authoritative data*. When a role needs a specific value (test
command, API spec, file path), have an upstream role write it into the job
doc rather than deriving it at runtime.

---

## 7. Total token usage can increase even when per-role optimizations succeed

Run 8 had 22% *more* total cached tokens than run 1 despite LCH dropping 87%.
Cause: the pipeline generated 19% more code (better implementations), and
more code = larger codebase = more files read by IMPLEMENTOR and TESTER at
integration time.

Prompt overhead optimizations don't help if the agent's *workload* is growing.
The IMPLEMENTOR/integrate (TOP) task alone went from 198K → 1,083K cached
(5.4×) because it read an entire assembled codebase before wiring it together.

**Implication:** measure the right thing. "Total cached tokens per run" conflates
prompt overhead (reducible) with workload cost (inherent to what the agent is
doing). Track them separately.

---

## 8. Scope handoff history to the active decomposition frame, not the full run

A flat append-only handoff list causes sibling components to share each
other's implementation context. Component A's IMPLEMENTOR handoff is visible
to Component B's ARCHITECT — noise that can dilute or distort design decisions.

Fix: maintain a frame stack alongside the handoff list. When DECOMPOSE_HANDLER
fires, push a frame anchored at the current handoff index. When
LEAF_COMPLETE_HANDLER advances to a sibling, truncate the handoff list back to
the frame anchor (discarding the completed component's history). When advancing
out of a composite, pop the frame.

**Result:** each component sees only the design lineage that produced it —
parent decomposition rationale is preserved, but sibling implementation details
are discarded.

---

## Summary Table

| Finding | Mechanism | Impact |
|---------|-----------|--------|
| Strip handoff from handler roles | `no_history` per role in state machine JSON | LCH: −95% cached tokens |
| Internal agents for deterministic roles | Python function instead of subprocess | LCH: −100% tokens, −15s/invocation |
| Set `cwd=/tmp` | Prevents CLAUDE.md injection via upward walk | −~3,500 tokens/invocation |
| Constrain what agents read | Test Command in job doc; TESTER runs verbatim | TESTER: TBD (run 11 pending) |
| Frame-scoped handoff history | frame_stack with truncation on sibling advance | Cleaner context, no sibling bleed |
| Workload cost is separate from prompt overhead | — | Measure separately; integration tasks are inherently expensive |
