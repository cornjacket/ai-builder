# Infra Smoke Test

Validates the gold test framework helpers without running the pipeline.
Uses a committed minimal stub binary as the fixture.

Run this before any full regression pipeline run to confirm the framework
itself is sound. It completes in under 15 seconds.

## Run

```bash
go test -v ./infra-smoke/smoke/
```

Run from `tests/regression/` (where `go.work` lives), or from the repo root.

## What It Tests

| Test | What it verifies |
|------|-----------------|
| `TestFindMainPackage` | Locates a `package main` directory under the fixture root |
| `TestFindMainPackages` | Returns exactly one main package (no drift) |
| `TestBuildBinary` | `go build` succeeds on the fixture binary |
| `TestWaitReady/TimesOutWhenNoListener` | Returns error after timeout when no server is up |
| `TestWaitReady/DetectsLiveListener` | Returns nil when the stub server is running |
| `TestMustDo` | Sends a GET to the stub and receives 200 |
| `TestExtractField` | Field extraction from JSON objects, including fallback keys |

## Layout

```
infra-smoke/
    fixture/            Committed stub binary source
        go.mod
        cmd/stub/
            main.go     HTTP server; PORT env var (default 9099)
    smoke/              Test package
        go.mod
        smoke_test.go
    README.md           This file
```
