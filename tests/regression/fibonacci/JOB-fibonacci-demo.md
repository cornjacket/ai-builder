# Job: Fibonacci Package Demo

Complexity: atomic

## Goal

Build a correct, importable Golang package that computes Fibonacci numbers.

- Package name: `fibonacci`
- Public function: `Compute(n int) []int`
- The package should live in a subdirectory named `fibonacci/`
- Include a `fibonacci_test.go` file with table-driven tests

---

## Execution Log

| # | Role | Agent | Description | Ended | Elapsed | Tokens In | Tokens Out | Tokens Cached |
|---|------|-------|-------------|-------|---------|-----------|------------|---------------|
| 1 | ARCHITECT | claude | fibonacci | 22:40:12 | 29s | 3 | 1,250 | 28,876 |
| 2 | DOCUMENTER_POST_ARCHITECT | internal | fibonacci | 22:40:12 | 0s | 0 | 0 | 0 |
| 3 | IMPLEMENTOR | claude | fibonacci | 22:40:35 | 22s | 6 | 1,194 | 80,643 |
| 4 | DOCUMENTER_POST_IMPLEMENTOR | internal | fibonacci | 22:40:35 | 0s | 0 | 0 | 0 |
| 5 | TESTER | claude | fibonacci | 22:40:48 | 13s | 3 | 215 | 27,673 |

## Design

- **Language:** Go
- **Package name:** `fibonacci`
- **Public function signature:** `Compute(n int) []int`
- **Input:** `n int` — the number of Fibonacci numbers to return
- **Output:** `[]int` — a slice containing the first `n` Fibonacci numbers in ascending order, starting with 0, 1, 1, 2, 3, …
- **Edge cases to handle:**
  - `n <= 0`: return an empty slice (`[]int{}`)
  - `n == 1`: return `[]int{0}`
  - `n == 2`: return `[]int{0, 1}`
- **Files to produce:**
  - `go.mod` — module declaration (`module fibonacci-demo`, `go 1.21`)
  - `fibonacci/fibonacci.go` — package implementation
  - `fibonacci/fibonacci_test.go` — table-driven tests covering edge cases and representative values
- **Expected outputs for verification:**
  - `Compute(-1)` → `[]int{}`
  - `Compute(0)` → `[]int{}`
  - `Compute(1)` → `[]int{0}`
  - `Compute(2)` → `[]int{0, 1}`
  - `Compute(5)` → `[]int{0, 1, 1, 2, 3}`
  - `Compute(10)` → `[]int{0, 1, 1, 2, 3, 5, 8, 13, 21, 34}`
- **No external dependencies** — use only the Go standard library.
- **Module:** the package lives at `fibonacci/` relative to the repo root passed to the pipeline; the surrounding `go.mod` declares the module.

---

## Acceptance Criteria

1. `go build ./...` completes with no errors.
2. `go test ./fibonacci/` passes with no failures.
3. `Compute(-1)` returns `[]int{}`.
4. `Compute(0)` returns `[]int{}`.
5. `Compute(1)` returns `[]int{0}`.
6. `Compute(2)` returns `[]int{0, 1}`.
7. `Compute(5)` returns `[]int{0, 1, 1, 2, 3}`.
8. `Compute(10)` returns `[]int{0, 1, 1, 2, 3, 5, 8, 13, 21, 34}`.
9. The `fibonacci_test.go` file uses a table-driven test structure covering at least the cases above.

---

## Test Command

```
cd /Users/david/Go/src/github.com/cornjacket/ai-builder/sandbox/fibonacci-output && go test ./fibonacci/
```

---

## Suggested Tools

```
go build ./...
go test ./fibonacci/
```

## Run Summary

| Field          | Value |
|----------------|-------|
| Task           | fibonacci |
| Start          | 2026-03-25 20:44:54 |
| End            | 2026-03-25 20:46:02 |
| Total time     | 1m 07s |
| Invocations    | 3 |
| Tokens in      | 12 |
| Tokens out     | 2,431 |
| Tokens cached  | 136,565 |
| Tokens total   | 139,008 |

### Invocations

| # | Role | Agent | Description | Ended | Elapsed | Tokens In | Tokens Out | Tokens Cached |
|---|------|-------|-------------|-------|---------|-----------|------------|---------------|
| 1 | ARCHITECT | claude | fibonacci | 20:45:14 | 20s | 3 | 1,185 | 28,668 |
| 2 | IMPLEMENTOR | claude | fibonacci | 20:45:42 | 27s | 6 | 1,047 | 80,269 |
| 3 | TESTER | claude | fibonacci | 20:46:02 | 19s | 3 | 199 | 27,628 |

### Per-Role Totals

| Role | Count | Total Time | Avg/Invocation |
|------|-------|------------|----------------|
| ARCHITECT | 1 | 20s | 20s |
| IMPLEMENTOR | 1 | 27s | 27s |
| TESTER | 1 | 19s | 19s |

### Token Usage by Role

| Role | Tokens In | Tokens Out | Tokens Cached | Total |
|------|-----------|------------|---------------|-------|
| ARCHITECT | 3 | 1,185 | 28,668 | 29,856 |
| IMPLEMENTOR | 6 | 1,047 | 80,269 | 81,322 |
| TESTER | 3 | 199 | 27,628 | 27,830 |
| **Total** | **12** | **2,431** | **136,565** | **139,008** |

### Invocations by Agent

| Agent | Count |
|-------|-------|
| claude | 3 |

## Run Summary

| Field          | Value |
|----------------|-------|
| Task           | fibonacci |
| Start          | 2026-03-25 21:53:58 |
| End            | 2026-03-25 21:54:58 |
| Total time     | 59s |
| Invocations    | 5 |
| Tokens in      | 13 |
| Tokens out     | 2,506 |
| Tokens cached  | 153,967 |
| Tokens total   | 156,486 |

### Invocations

| # | Role | Agent | Description | Ended | Elapsed | Tokens In | Tokens Out | Tokens Cached |
|---|------|-------|-------------|-------|---------|-----------|------------|---------------|
| 1 | ARCHITECT | claude | fibonacci | 21:54:24 | 25s | 3 | 1,194 | 28,668 |
| 2 | DOCUMENTER_POST_ARCHITECT | internal | fibonacci | 21:54:24 | 0s | 0 | 0 | 0 |
| 3 | IMPLEMENTOR | claude | fibonacci | 21:54:47 | 22s | 7 | 1,122 | 97,677 |
| 4 | DOCUMENTER_POST_IMPLEMENTOR | internal | fibonacci | 21:54:47 | 0s | 0 | 0 | 0 |
| 5 | TESTER | claude | fibonacci | 21:54:58 | 11s | 3 | 190 | 27,622 |

### Per-Role Totals

| Role | Count | Total Time | Avg/Invocation |
|------|-------|------------|----------------|
| ARCHITECT | 1 | 25s | 25s |
| DOCUMENTER_POST_ARCHITECT | 1 | 0s | 0s |
| IMPLEMENTOR | 1 | 22s | 22s |
| DOCUMENTER_POST_IMPLEMENTOR | 1 | 0s | 0s |
| TESTER | 1 | 11s | 11s |

### Token Usage by Role

| Role | Tokens In | Tokens Out | Tokens Cached | Total |
|------|-----------|------------|---------------|-------|
| ARCHITECT | 3 | 1,194 | 28,668 | 29,865 |
| DOCUMENTER_POST_ARCHITECT | 0 | 0 | 0 | 0 |
| IMPLEMENTOR | 7 | 1,122 | 97,677 | 98,806 |
| DOCUMENTER_POST_IMPLEMENTOR | 0 | 0 | 0 | 0 |
| TESTER | 3 | 190 | 27,622 | 27,815 |
| **Total** | **13** | **2,506** | **153,967** | **156,486** |

### Invocations by Agent

| Agent | Count |
|-------|-------|
| claude | 3 |
| internal | 2 |

## Run Summary

| Field          | Value |
|----------------|-------|
| Task           | fibonacci |
| Start          | 2026-03-25 22:39:43 |
| End            | 2026-03-25 22:40:48 |
| Total time     | 1m 05s |
| Invocations    | 5 |
| Tokens in      | 12 |
| Tokens out     | 2,659 |
| Tokens cached  | 137,192 |
| Tokens total   | 139,863 |

### Invocations

| # | Role | Agent | Description | Ended | Elapsed | Tokens In | Tokens Out | Tokens Cached |
|---|------|-------|-------------|-------|---------|-----------|------------|---------------|
| 1 | ARCHITECT | claude | fibonacci | 22:40:12 | 29s | 3 | 1,250 | 28,876 |
| 2 | DOCUMENTER_POST_ARCHITECT | internal | fibonacci | 22:40:12 | 0s | 0 | 0 | 0 |
| 3 | IMPLEMENTOR | claude | fibonacci | 22:40:35 | 22s | 6 | 1,194 | 80,643 |
| 4 | DOCUMENTER_POST_IMPLEMENTOR | internal | fibonacci | 22:40:35 | 0s | 0 | 0 | 0 |
| 5 | TESTER | claude | fibonacci | 22:40:48 | 13s | 3 | 215 | 27,673 |

### Per-Role Totals

| Role | Count | Total Time | Avg/Invocation |
|------|-------|------------|----------------|
| ARCHITECT | 1 | 29s | 29s |
| DOCUMENTER_POST_ARCHITECT | 1 | 0s | 0s |
| IMPLEMENTOR | 1 | 22s | 22s |
| DOCUMENTER_POST_IMPLEMENTOR | 1 | 0s | 0s |
| TESTER | 1 | 13s | 13s |

### Token Usage by Role

| Role | Tokens In | Tokens Out | Tokens Cached | Total |
|------|-----------|------------|---------------|-------|
| ARCHITECT | 3 | 1,250 | 28,876 | 30,129 |
| DOCUMENTER_POST_ARCHITECT | 0 | 0 | 0 | 0 |
| IMPLEMENTOR | 6 | 1,194 | 80,643 | 81,843 |
| DOCUMENTER_POST_IMPLEMENTOR | 0 | 0 | 0 | 0 |
| TESTER | 3 | 215 | 27,673 | 27,891 |
| **Total** | **12** | **2,659** | **137,192** | **139,863** |

### Invocations by Agent

| Agent | Count |
|-------|-------|
| claude | 3 |
| internal | 2 |
