# Lesson 005 — Abstract Test Infrastructure to Support Local Dev and CI Independently

**Category:** architecture
**Source project:** cornjacket-platform
**Date:** 2026-02-10

## Context

When designing integration tests (Spec 010), the question arose: should tests use docker-compose (developer runs `docker compose up` before testing) or testcontainers (tests programmatically start their own containers)?

Both have clear strengths in different contexts:

| | docker-compose | testcontainers |
|---|---|---|
| **Local dev** | Fast iteration — containers already running, 0s startup | 5-10s startup per container per test run |
| **CI** | Requires orchestration — `docker compose up`, health checks, port management | Self-contained — `go test` is the only command needed |
| **Isolation** | Shared containers — stale data from manual testing can leak into test runs | Fresh container per run — guaranteed clean state |
| **Port conflicts** | Hardcoded ports — fails if another process uses the same port | Random port assignment — no conflicts |
| **Parallel CI jobs** | Multiple jobs can't share one docker-compose stack | Each job spins up independent containers |
| **Dependencies** | Already in the repo | Adds a new library (e.g., testcontainers-go) |

The insight: these aren't mutually exclusive choices. They're deployment strategies for the same test logic, and the boundary between them can be a thin abstraction.

## Lesson

**Put all test infrastructure setup behind helper functions, so the test files never know how their dependencies were started.**

Concretely, create a `testutil` package (or equivalent) with functions like:

```go
func NewTestPool(t *testing.T) *pgxpool.Pool       // Postgres connection
func TestBrokers() []string                          // Kafka/Redpanda broker addresses
func RunMigrations(t *testing.T, pool *pgxpool.Pool, dir string)
func TruncateTables(t *testing.T, pool *pgxpool.Pool, tables ...string)
```

Test files call these helpers and never reference `localhost:5432` or container startup logic directly. This creates a **seam**: swapping docker-compose for testcontainers means changing only the helper implementations — zero changes to test files.

### The practical split

- **Local development (Phase 1):** docker-compose. Fast iteration, containers already running, no new dependencies.
- **CI pipelines (Phase 3+):** testcontainers. Self-contained, no orchestration step, parallel-safe.

This isn't a "pick one" decision — it's a "start simple, migrate cheaply" strategy. The abstraction layer makes the migration cost near-zero.

### How the seam works in practice

**Phase 1 (docker-compose):**
```go
func NewTestPool(t *testing.T) *pgxpool.Pool {
    url := os.Getenv("INTEGRATION_DB_URL")
    if url == "" {
        url = "postgres://cornjacket:cornjacket@localhost:5432/cornjacket?sslmode=disable"
    }
    pool, err := pgxpool.New(context.Background(), url)
    // ...
    return pool
}
```

**Phase 3 (testcontainers) — same function signature:**
```go
func NewTestPool(t *testing.T) *pgxpool.Pool {
    ctx := context.Background()
    pg, err := postgres.Run(ctx, "timescale/timescaledb:2.23.0-pg18")
    t.Cleanup(func() { pg.Terminate(ctx) })
    url, _ := pg.ConnectionString(ctx)
    pool, err := pgxpool.New(ctx, url)
    // ...
    return pool
}
```

Test files don't change. The 22 integration tests written in Phase 1 work identically in Phase 3's CI pipeline.

## Decision Guidance

When writing integration tests for a project that will eventually have CI:

1. **Never hardcode infrastructure addresses in test files.** Always go through a helper.
2. **Start with whatever infrastructure you already have** (docker-compose, local install, etc.). Don't add testcontainers until you need self-contained CI.
3. **Design the helper API as if testcontainers exist**, even when the implementation is a simple `localhost` connection. The function signatures should accept `*testing.T` so they can register cleanup via `t.Cleanup()` — this is free for docker-compose (no-op cleanup) and essential for testcontainers.
4. **Migrate when CI arrives**, not before. The cost of premature testcontainers adoption is slower local development with no CI to benefit from it.

## Related Lessons

- [001 — Separate Meta-Learning from Project Repos](001-separate-meta-learning-from-project-repos.md): This lesson is a reusable testing pattern, not a cornjacket-specific decision.
