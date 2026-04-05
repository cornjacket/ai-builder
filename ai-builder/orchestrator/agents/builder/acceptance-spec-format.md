# acceptance-spec format guide

This document describes the format that `acceptance-spec.json` and
`acceptance-spec.md` must conform to, and what ACCEPTANCE_SPEC_WRITER requires
from a build spec in order to produce them.

---

## acceptance-spec.json

Produced by ACCEPTANCE_SPEC_WRITER. Consumed by the spec coverage checker.
Must validate against `acceptance-spec-schema.json`.

**Schema (v1, HTTP only):**

```json
{
  "version": 1,
  "endpoints": [
    {
      "method": "POST",
      "path": "/roles",
      "status_codes": [201, 400]
    },
    {
      "method": "GET",
      "path": "/roles",
      "status_codes": [200]
    },
    {
      "method": "GET",
      "path": "/roles/{id}",
      "status_codes": [200, 404]
    }
  ]
}
```

**Rules:**
- `method` — uppercase HTTP verb
- `path` — exact path from the build spec, starting with `/`; path parameters
  use `{param}` notation
- `status_codes` — all status codes called out in the build spec for this
  endpoint (both success and notable error codes); at least one required

---

## acceptance-spec.md

Human-readable version of the spec. Written verbatim from the build spec's
API contract section. Consumed by ARCHITECT agents (DECOMPOSE and TOP integrate
modes) to prevent drift.

There is no fixed schema for `acceptance-spec.md` — it is a direct copy of
the relevant sections from the build spec. The ARCHITECT reads it as
reference material.

---

## Requirements on the build spec

ACCEPTANCE_SPEC_WRITER reads the build spec's `## Goal` and `## Context`
sections. To be parseable, the build spec must list its HTTP endpoints
explicitly, including:

- HTTP method and path for each endpoint
- At least one expected status code per endpoint
- Field names exactly as they should appear in requests and responses

**Non-HTTP interfaces:** if the build spec describes interfaces other than
HTTP (e.g. CLI commands, message queue consumers, gRPC, library APIs),
ACCEPTANCE_SPEC_WRITER will halt the pipeline with an error. A new acceptance
spec schema must be defined and a corresponding writer/checker pair implemented
before that build spec can be run through the builder pipeline.

---

## Files written to output_dir

Both files are written to the root of the pipeline's `output_dir` at the path
known by convention:

| File | Path |
|------|------|
| `acceptance-spec.md` | `<output_dir>/acceptance-spec.md` |
| `acceptance-spec.json` | `<output_dir>/acceptance-spec.json` |

Downstream ARCHITECT agents locate them by this convention — no path injection
by the orchestrator is required.
