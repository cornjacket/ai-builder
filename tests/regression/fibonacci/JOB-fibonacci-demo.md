# Job: Fibonacci Package Demo

## Goal

Build a correct, importable Golang package that computes Fibonacci numbers.

- Package name: `fibonacci`
- Public function: `Compute(n int) []int`
- The package should live in a subdirectory named `fibonacci/`
- Include a `fibonacci_test.go` file with table-driven tests

---

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

## Suggested Tools

```
go build ./...
go test ./fibonacci/
```
