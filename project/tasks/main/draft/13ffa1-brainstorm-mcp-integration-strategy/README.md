# Task: brainstorm-mcp-integration-strategy

| Field    | Value                |
|----------|----------------------|
| Status   | draft           |
| Epic     | main             |
| Tags     | mcp, orchestrator, architecture             |
| Parent   | —           |
| Priority | HIGH         |

## Description

Produce an architectural recommendation for MCP integration across the
platform's agent roles. Scripts work well under supervised workflows, but as
agents operate with less human oversight the soft constraint of "only use
these scripts" becomes a risk. MCP enforces tool boundaries at the protocol
level, not the prompt level.

**Platform context:**
- Agents are spawned as `claude -p` subprocesses with independent 200K token
  budgets
- Each agent operates within a git worktree with scoped CLAUDE.md context
- Agents operate at different abstraction levels: orchestrator (Oracle/PM),
  implementer (ARCHITECT, IMPLEMENTOR), reviewer (TESTER, human gate)
- Current tooling uses purpose-built scripts as constrained toolsets per role

**Questions to resolve:**

1. **Where does MCP earn its cost?** Which abstraction levels warrant MCP
   over scripts — specifically where the cost of an agent going off-script
   exceeds the cost of building and maintaining an MCP boundary.

2. **Tight scoping per role.** How to scope MCP servers to minimize context
   cost — avoiding the wholesale loading problem of general-purpose servers.
   Each role should see only the tools it legitimately needs.

3. **Differentiated trust levels.** Whether the orchestrator, implementer,
   and reviewer roles have meaningfully different trust levels that warrant
   different constraint mechanisms. The orchestrator may need broader access
   to coordinate; the implementer should be narrowly constrained.

4. **Purpose-built vs. direct script access.** What a purpose-built MCP
   server for this platform would expose at each level, versus what remains
   as direct script access within a sandboxed worktree.

**Deliverable:**
A tiered recommendation mapping agent roles to constraint mechanisms (MCP
server / scoped scripts / direct access), with token cost implications noted
for each tier. Output belongs in `docs/` as a design reference.

## Documentation

Promote output to `docs/mcp-integration-strategy.md` once the brainstorm
is resolved into a recommendation.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

This is a parallel subagent task — it can be run independently of the
oracle/pipeline design work and its output feeds into both role definitions
and the orchestrator design.

Related tasks:
- `37a660-design-oracle-and-pipeline-phases` — MCP boundaries affect how
  the orchestrator spawns and constrains each role
- `6fdb3a-consolidate-role-definitions` — role definitions will need to
  specify which tools (scripts vs. MCP) each role is permitted to use
- `2c2130-design-subagent-cwd-convention` — CWD and tool access are related
  constraints on subagent scope

Key tension to resolve: MCP adds protocol-level enforcement and auditability
but at the cost of server implementation overhead and potential context
bloat if servers are not scoped tightly. Scripts are cheap to write but
only prompt-level constraints — an agent can ignore them.
