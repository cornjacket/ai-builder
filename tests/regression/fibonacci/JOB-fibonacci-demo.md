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
| 1 | ARCHITECT | claude | fibonacci | 20:45:14 | 20s | 3 | 1,185 | 28,668 |
| 2 | IMPLEMENTOR | claude | fibonacci | 20:45:42 | 27s | 6 | 1,047 | 80,269 |
| 3 | TESTER | claude | fibonacci | 20:46:02 | 19s | 3 | 199 | 27,628 |

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
