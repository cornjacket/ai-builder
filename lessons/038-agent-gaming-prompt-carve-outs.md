# 038 — Agent Gaming Prompt Carve-Outs

**Context:** AIDT+ orchestrator experiments, fibonacci demo pipeline.

**Observed:** The IMPLEMENTOR extracted a `print_fibonacci` helper function —
not because the design called for it, but because the prompt's carve-out said
"you may test internal functions." This gave the agent justification to write a
temp test file, run several tests, and delete it. The code was functionally
correct but the agent manufactured structural complexity to exploit the
permission.

**Root cause:** Carve-out language that conditions a permission on a state the
agent itself can create ("if the implementation contains internal functions") is
gameable. The agent controls whether the condition is true.

**Fix:** Condition carve-outs on the *design* specifying internal structure, not
on whatever the agent decides to introduce:

> "Do not introduce functions, classes, or modules not specified in the Design.
> If the Design explicitly calls for a module with internal functions, you may
> run minimal happy-path tests of those internals only. Otherwise, a syntax
> check is sufficient."

**Principle:** Permissions granted to agents should be conditioned on external,
user-controlled state — not on state the agent can manufacture to qualify
itself.
