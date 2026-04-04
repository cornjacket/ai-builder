# Task: regression-run-in-docker

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Created     | 2026-04-03            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Run each regression in an isolated Docker container so that target services
bind to ports inside the container rather than the host network, eliminating
port conflicts between concurrent regression runs and between regressions and
other locally running services.

## Context

**The problem today:**
The pipeline launches target services (e.g. the platform-monolith API server)
that bind to fixed ports on the host (e.g. 8081, 8082). When a prior
regression run leaves a process listening on those ports, the next run fails
immediately with `address already in use`. We hit this during the
platform-monolith regression when the gold test binary from the first run was
still listening on 8081 when the second run started.

The current workaround is to manually kill the stale process with
`lsof -ti :<port> | xargs kill -9`. This is fragile and does not scale to
parallel worktrees running regressions simultaneously.

**Proposed solution:**
Wrap the regression run (reset.sh → orchestrator → gold tests) inside a Docker
container. Each container gets its own network namespace, so services bind to
the same port numbers inside the container without conflicting with other
containers or the host. No port-mapping to the host is needed for regressions
that only require internal service-to-service communication (orchestrator →
target API).

**Scope:**
- `tests/regression/*/reset.sh` — launch services inside container rather than
  directly on host
- `tests/regression/*/run.sh` — invoke orchestrator inside or against the
  container; gold tests may run inside or connect via mapped port
- Container lifecycle: start on `reset.sh`, stop/remove on regression complete
  or on explicit teardown
- Must remain compatible with the regression manager session (Option C in
  15bff5) — the overlord session would `docker run` rather than shell directly

**Open questions:**
- Should the entire regression (orchestrator + target) run inside one container,
  or should the target service run in a container while the orchestrator runs on
  the host?
- Does the orchestrator need network access to external AI APIs from inside the
  container? (Yes — needs outbound internet; host networking or explicit proxy
  may be required.)
- Are gold tests run inside the container or on the host against a mapped port?
- How does this interact with the always-on-recording feature (`afed3c`) — git
  commits inside a container need the repo mounted.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
