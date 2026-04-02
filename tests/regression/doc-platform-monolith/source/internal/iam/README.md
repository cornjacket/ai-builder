# iam

Purpose: Identity and access management service for the platform. Exposes user lifecycle (registration, authentication) and RBAC authorisation over HTTP on port 8082.
Tags: architecture, design

## File Index

| File | Description |
|------|-------------|
| `iam.go` | Package entry point; `New()` wires sub-components and returns `http.Handler` |
| `lifecycle/lifecycle.go` | In-memory user store and token session management; registers `/users` and `/auth` routes |
| `authz/authz.go` | In-memory role store and user-role assignments; registers `/roles`, `/users/{id}/roles`, and `/authz/check` routes |

## Overview

The `iam` package is an internal composite composed of two atomic sub-packages:

- **lifecycle** — owns user CRUD and auth tokens. Users are stored in a `map[string]User` keyed by UUID. Passwords are stored as bcrypt hashes. Login issues an opaque token (UUID); logout invalidates it. All state is guarded by a `sync.RWMutex`.

- **authz** — owns RBAC. Roles have a name and a set of permission strings. Users can be assigned multiple roles. `POST /authz/check` resolves whether a user has a given permission by walking their assigned roles. State is in-memory with its own mutex. Role IDs assigned as UUIDs. User IDs are opaque strings (no direct import of lifecycle — loose coupling via string IDs).

- **integrate** (`iam.go`) — instantiates both sub-packages, registers all routes on a single `http.ServeMux`, and returns the mux as `http.Handler`. The top-level `main.go` binds this handler to `:8082`.

### Route Summary

| Method | Path | Handler |
|--------|------|---------|
| POST | /users | lifecycle |
| GET | /users/{id} | lifecycle |
| DELETE | /users/{id} | lifecycle |
| POST | /auth/login | lifecycle |
| POST | /auth/logout | lifecycle |
| POST | /roles | authz |
| GET | /roles | authz |
| POST | /users/{id}/roles | authz |
| GET | /users/{id}/roles | authz |
| POST | /authz/check | authz |

### Design Constraints

- No external database; all state lives in process memory.
- Go module: `github.com/cornjacket/platform`; packages at `internal/iam`, `internal/iam/lifecycle`, `internal/iam/authz`.
- The `integrate` component does not add a subdirectory — `iam.go` lives directly in the output directory alongside the sub-package directories.
