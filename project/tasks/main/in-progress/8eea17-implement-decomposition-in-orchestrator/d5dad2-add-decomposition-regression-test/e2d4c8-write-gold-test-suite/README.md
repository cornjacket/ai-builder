# Subtask: write-gold-test-suite

| Field       | Value                                                                        |
|-------------|------------------------------------------------------------------------------|
| Status      | complete                                                                     |
| Epic        | main                                                                         |
| Tags        | —                                                                            |
| Parent      | 8eea17-implement-decomposition-in-orchestrator/d5dad2-add-decomposition-regression-test |
| Priority    | —                                                                            |
| Complexity  | —                                                                            |
| Stop-after  | false                                                                        |

## Description

Write the gold test suite that validates the pipeline's output. The gold tests
run against whatever code the pipeline produces — they cannot assume specific
file names or package structure, only the observable HTTP behaviour.

**Gold tests must verify:**
- `POST /users` creates a user and returns it with a generated ID
- `GET /users/{id}` returns the user by ID; returns 404 for unknown ID
- `PUT /users/{id}` updates a user; returns 404 for unknown ID
- `DELETE /users/{id}` deletes a user; returns 404 for unknown ID
- Service listens on port `8080`
- All responses are JSON

**Implementation:** a Go test file using `net/http` that starts the service
binary, exercises each endpoint, and asserts on status codes and response bodies.

**Output:** `tests/regression/user-service/gold/gold_test.go`

**Note on multi-component output:** this test suite validates only the
assembled binary behaviour, not the internal component structure. The gold
tests must compile and run against any correct implementation regardless of
how the ARCHITECT decomposed it.

## Notes

Must be written before `run-pipeline-and-verify` but can be written before
the pipeline has run — the gold tests are independent of the pipeline output.
