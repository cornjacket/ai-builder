# Subtask: write-job-document-template

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

Write the job document that the test pre-seeds for the pipeline, simulating
what Oracle would produce. The job document uses the `JOB-service-build.md`
template (decompose mode) and describes the user management HTTP service.

**Service specification (fixed constraints):**
- Language: Go
- Port: `8080`
- Routes: `POST /users`, `GET /users/{id}`, `PUT /users/{id}`, `DELETE /users/{id}`
- Response format: JSON
- Storage: in-memory (no database, no persistence)
- No authentication or authorisation

**The job document must NOT specify components.** The ARCHITECT decides the
decomposition. The Goal section describes the service; the Components section
is left with only the table header so ARCHITECT fills it in.

**Output:** `tests/regression/user-service/work/JOB-user-service.md`

`reset.sh` copies this file into the pipeline output directory before each run.

## Notes

The service spec is intentionally minimal so the ARCHITECT's decomposition
choices are the thing being tested, not conformance to a spec.
