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
- **Public function signature:** `func Compute(n int) []int`
- **Input:** `n int` — the count of Fibonacci numbers to return
- **Output:** a slice of the first `n` Fibonacci numbers in ascending order, starting from 0. For example, `Compute(7)` → `[0, 1, 1, 2, 3, 5, 8]`
- **Edge cases to handle:**
  - `n <= 0`: return an empty slice `[]int{}`
  - `n == 1`: return `[]int{0}`
  - `n == 2`: return `[]int{0, 1}`
- **Files to produce:**
  - `fibonacci/fibonacci.go` — package implementation containing `Compute`
  - `fibonacci/fibonacci_test.go` — table-driven tests covering edge cases and normal cases
- **Expected outputs for verification:**
  - `Compute(0)` → `[]`
  - `Compute(1)` → `[0]`
  - `Compute(2)` → `[0, 1]`
  - `Compute(5)` → `[0, 1, 1, 2, 3]`
  - `Compute(10)` → `[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]`

### Implementation Steps

1. Create the `fibonacci/` directory and `fibonacci.go` with `package fibonacci` and the `Compute` function.
2. Implement `Compute`: handle `n <= 0` first, then seed the slice with `[0]` (and `[0, 1]` for `n >= 2`), then loop appending `a[i-1] + a[i-2]` until the slice has `n` elements.
3. Create `fibonacci/fibonacci_test.go` with a table-driven test that iterates over the expected-output cases above plus at least one larger case (`n == 10`).

---

## Acceptance Criteria

1. The package compiles without errors (`go build ./fibonacci/`).
2. All tests pass (`go test ./fibonacci/`).
3. `Compute(n)` returns a slice of exactly `n` elements for any `n >= 0`.
4. The sequence starts at 0 and each element equals the sum of the two preceding elements.
5. `Compute(0)` and `Compute(-1)` both return a non-nil empty slice.
6. The test file uses table-driven style with at least 5 distinct cases, including `n=0`, `n=1`, `n=2`, `n=5`, and `n=10`.
