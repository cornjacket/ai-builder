# 040 — Brainstorm to File, Not Chat

**Context:** Pipeline repurposing design discussion (doc/review/update pipelines).

**Observed:** A lengthy design discussion about repurposing the pipeline for
documentation generation, code review, and codebase updates happened entirely
in chat. Key design decisions — the `"type": "file"` component, the scratch pad
pattern, the POST_INTEGRATE_HANDLER, three directory shapes — were made verbally
and had to be reconstructed into `sandbox/brainstorm-pipeline-repurposing.md`
after the fact. The reconstructed document required inference to fill gaps that
were clear during the conversation but not explicitly stated.

**Problem:** Chat is ephemeral. Design decisions made in conversation are lossy:
- Nuance gets flattened during reconstruction
- The order of reasoning is lost
- Gaps appear that weren't visible during the live discussion
- Context rot means neither human nor AI can reliably reconstruct what was said

**Fix:** When a brainstorm session begins, immediately create
`sandbox/brainstorm-{subject}.md` and write decisions into it in real time as
the discussion unfolds. The file is the authoritative record; chat is the medium
for thinking out loud.

**Rule added to CLAUDE.md:**
> When the user says "let's brainstorm on X", "brainstorm X", or similar,
> immediately create `sandbox/brainstorm-{subject}.md` before the discussion
> begins. Write design decisions to that file in real time as the discussion
> unfolds — do not discuss first and reconstruct afterward. The file is the
> record; chat is ephemeral.

**Takeaway:** Any insight worth having is worth capturing the moment it occurs.
The cost of opening a file is zero. The cost of reconstructing a conversation
is non-trivial and always lossy.
