# Lesson 006 — Make Milestone Tags Explicit Checklist Items

**Category:** process
**Source project:** cornjacket-platform
**Date:** 2026-02-10

## Context

In a multi-repo project (three Git repos sharing coordinated tags at phase boundaries), the tagging policy existed as an ADR and a policy section in PROJECT.md — but the actual act of tagging wasn't a line item in any phase checklist. The assumption was "we'll remember to tag when the phase is done."

This came up when adding phase milestone tasks. The tagging policy (ADR-0011) specified the format and rules, but without a visible checkbox, the tag was the one action most likely to be forgotten — especially because it happens after all the "real work" is complete, when momentum is toward starting the next phase.

## Lesson

**In multi-repo projects, make milestone tagging an explicit last-item task in every phase checklist.** Don't rely on policy documents alone.

This applies more broadly: **any cross-repo coordination action should be a visible checklist item, not an implicit consequence of a policy.** Policies describe what should happen. Checklists ensure it happens.

### Why the last task matters

- It's a **gate** — you can't check it off until you've verified all other work is done
- It's **visible** — unlike a policy buried in an ADR, a checkbox in the active checklist gets attention
- It's **auditable** — if the tag is missing from one repo, the checklist shows the task was never completed
- It prevents **partial tagging** — listing all repos by name (`platform-services, platform-docs, platform-infra`) makes it explicit that all three need tags, not just the one you were working in

### Generalizing beyond initial project phases

The same pattern applies to any major development effort that gets broken into phases — feature epics, migration projects, major refactors. If the work spans multiple repos and multiple weeks, it benefits from:

1. Formal phase breakdown with a checklist
2. Milestone tags at each phase boundary
3. The tagging task as an explicit last item

## Decision Guidance

When structuring phased work in a multi-repo project:

1. Define phases with clear deliverables and checklists
2. Add "Tag `phase-N-description` on [list all repos by name]" as the last task in each phase
3. Name all repos explicitly — don't say "tag all repos," say which ones
4. Treat the tag task as a completion gate: it's what distinguishes "done with the work" from "done with the phase"

When this seems like overkill (single repo, single developer, small scope), it probably is. The value scales with repo count and team size. For a solo dev in a single repo, a git tag at the end of a feature branch is sufficient.

## Related Lessons

- [005 — Abstract Test Infrastructure for Local vs CI](005-abstract-test-infrastructure-for-local-vs-ci.md): Another case where explicit process structure prevents "we'll remember" failures.
