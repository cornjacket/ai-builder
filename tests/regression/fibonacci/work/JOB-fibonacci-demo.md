# Job: Fibonacci Package Demo

## Goal

Build a correct, importable Golang package that computes Fibonacci numbers.

- Package name: `fibonacci`
- Public function: `Compute(n int) []int`
- The package should live in a subdirectory named `fibonacci/`
- Include a `fibonacci_test.go` file with table-driven tests

---

## Design

- **Language:** Go (module-free package, compatible with `go test ./...`)
- **Package name:** `fibonacci`
- **Public function signature:** `func Compute(n int) []int`
- **Input:** `n int` — the number of Fibonacci terms to return
- **Output:** A slice of `n` integers containing the first `n` Fibonacci numbers in order, starting from 0
- **Edge cases to handle:**
  - `n <= 0`: return an empty slice `[]int{}`
  - `n == 1`: return `[]int{0}`
  - `n == 2`: return `[]int{0, 1}`
- **Files to produce:**
  1. `fibonacci/fibonacci.go` — package implementation containing `Compute`
  2. `fibonacci/fibonacci_test.go` — table-driven tests using the standard `testing` package
- **Expected outputs for verification:**
  - `Compute(0)` → `[]int{}`
  - `Compute(1)` → `[]int{0}`
  - `Compute(2)` → `[]int{0, 1}`
  - `Compute(5)` → `[]int{0, 1, 1, 2, 3}`
  - `Compute(8)` → `[]int{0, 1, 1, 2, 3, 5, 8, 13}`
  - `Compute(-1)` → `[]int{}`

### Implementation Steps

1. Create `fibonacci/fibonacci.go` with the `Compute` function:
   - Return empty slice for `n <= 0`
   - Seed the slice with `[0]` for `n == 1`
   - Seed the slice with `[0, 1]` for `n >= 2`, then iterate, appending `a[i-1] + a[i-2]` until the slice has `n` elements
2. Create `fibonacci/fibonacci_test.go` with a table-driven test covering the expected outputs above, using `reflect.DeepEqual` for slice comparison

---

## Acceptance Criteria

1. `fibonacci/fibonacci.go` exists and declares `package fibonacci`
2. `Compute` is exported and has signature `func Compute(n int) []int`
3. `fibonacci/fibonacci_test.go` exists and contains table-driven tests
4. `go test ./fibonacci/` passes with no failures
5. All expected outputs listed in the Design section are verified by tests:
   - `n <= 0` returns an empty (non-nil is acceptable) slice
   - `n == 1` returns `[0]`
   - `n == 5` returns `[0, 1, 1, 2, 3]`
   - `n == 8` returns `[0, 1, 1, 2, 3, 5, 8, 13]`
6. No external dependencies — only the standard library is used
