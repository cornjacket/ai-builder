# metrics

Purpose: HTTP ingestion service that records frontend user interaction events in memory and exposes them for retrieval. Listens on port 8081.
Tags: architecture, design

## File Index

| File | Description |
|------|-------------|
| `metrics.go` | Package-level `New()` constructor — wires store and handlers, returns an `http.Handler` |
| `store/store.go` | In-memory event store with thread-safe Add and List operations |
| `handlers/handlers.go` | HTTP handlers for POST /events and GET /events |

## Overview

The metrics package is internally composed of two sub-packages:

- **store** — owns the `Event` struct and all state. Generates UUIDs for new events. Safe for concurrent use via a `sync.RWMutex`.
- **handlers** — pure HTTP layer. Accepts a `store.Storer` interface so it has no import cycle back to the parent package. Encodes/decodes JSON; returns the documented status codes.

The package-level `New()` function in `metrics.go` instantiates a `store.Store`, injects it into the handlers, registers routes on a fresh `http.ServeMux`, and returns the mux. The caller (`cmd/platform/main.go`) wraps the returned handler in an `http.Server` listening on `:8081`.

### API contract

```
POST /events
  Request:  {"type":"click-mouse"|"submit-form","userId":string,"payload":{}}
  Response: 201 {"id":string,"type":string,"userId":string,"payload":{}}
  Errors:   400 on invalid JSON or unknown type

GET /events
  Response: 200 [{"id":string,"type":string,"userId":string,"payload":{}}]
            200 [] when no events have been recorded
```

### Data model

```go
type Event struct {
    ID      string                 `json:"id"`
    Type    string                 `json:"type"`
    UserID  string                 `json:"userId"`
    Payload map[string]interface{} `json:"payload"`
}
```
