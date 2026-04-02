package authz

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
)

func newTestMux() *http.ServeMux {
	mux := http.NewServeMux()
	New().RegisterRoutes(mux)
	return mux
}

func TestCreateRole(t *testing.T) {
	mux := newTestMux()
	body := `{"name":"admin","permissions":["read","write"]}`
	rec := httptest.NewRecorder()
	mux.ServeHTTP(rec, httptest.NewRequest("POST", "/roles", bytes.NewBufferString(body)))
	if rec.Code != http.StatusCreated {
		t.Fatalf("expected 201, got %d", rec.Code)
	}
	var r Role
	if err := json.NewDecoder(rec.Body).Decode(&r); err != nil {
		t.Fatal(err)
	}
	if r.ID == "" {
		t.Error("expected non-empty id")
	}
	if r.Name != "admin" {
		t.Errorf("expected name admin, got %s", r.Name)
	}
	if len(r.Permissions) != 2 {
		t.Errorf("expected 2 permissions, got %d", len(r.Permissions))
	}
}

func TestListRolesEmpty(t *testing.T) {
	mux := newTestMux()
	rec := httptest.NewRecorder()
	mux.ServeHTTP(rec, httptest.NewRequest("GET", "/roles", nil))
	if rec.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", rec.Code)
	}
	var roles []Role
	if err := json.NewDecoder(rec.Body).Decode(&roles); err != nil {
		t.Fatal(err)
	}
	if roles == nil {
		t.Error("expected [] not null")
	}
	if len(roles) != 0 {
		t.Errorf("expected 0 roles, got %d", len(roles))
	}
}

func TestListRolesTwoRoles(t *testing.T) {
	mux := newTestMux()
	for _, name := range []string{"admin", "viewer"} {
		body := `{"name":"` + name + `","permissions":[]}`
		rec := httptest.NewRecorder()
		mux.ServeHTTP(rec, httptest.NewRequest("POST", "/roles", bytes.NewBufferString(body)))
		if rec.Code != http.StatusCreated {
			t.Fatalf("create role: expected 201, got %d", rec.Code)
		}
	}
	rec := httptest.NewRecorder()
	mux.ServeHTTP(rec, httptest.NewRequest("GET", "/roles", nil))
	var roles []Role
	json.NewDecoder(rec.Body).Decode(&roles)
	if len(roles) != 2 {
		t.Errorf("expected 2 roles, got %d", len(roles))
	}
}

func createRole(t *testing.T, mux *http.ServeMux, name string, perms []string) Role {
	t.Helper()
	p, _ := json.Marshal(perms)
	body := `{"name":"` + name + `","permissions":` + string(p) + `}`
	rec := httptest.NewRecorder()
	mux.ServeHTTP(rec, httptest.NewRequest("POST", "/roles", bytes.NewBufferString(body)))
	if rec.Code != http.StatusCreated {
		t.Fatalf("createRole: expected 201, got %d", rec.Code)
	}
	var r Role
	json.NewDecoder(rec.Body).Decode(&r)
	return r
}

func TestAssignRoleValid(t *testing.T) {
	mux := newTestMux()
	role := createRole(t, mux, "admin", []string{"read"})
	body := `{"roleId":"` + role.ID + `"}`
	rec := httptest.NewRecorder()
	mux.ServeHTTP(rec, httptest.NewRequest("POST", "/users/u1/roles", bytes.NewBufferString(body)))
	if rec.Code != http.StatusCreated {
		t.Fatalf("expected 201, got %d", rec.Code)
	}
}

func TestAssignRoleUnknown(t *testing.T) {
	mux := newTestMux()
	body := `{"roleId":"nonexistent"}`
	rec := httptest.NewRecorder()
	mux.ServeHTTP(rec, httptest.NewRequest("POST", "/users/u1/roles", bytes.NewBufferString(body)))
	if rec.Code != http.StatusNotFound {
		t.Fatalf("expected 404, got %d", rec.Code)
	}
}

func TestUserRolesAfterAssign(t *testing.T) {
	mux := newTestMux()
	role := createRole(t, mux, "editor", []string{"read", "write"})
	body := `{"roleId":"` + role.ID + `"}`
	rec := httptest.NewRecorder()
	mux.ServeHTTP(rec, httptest.NewRequest("POST", "/users/u1/roles", bytes.NewBufferString(body)))
	if rec.Code != http.StatusCreated {
		t.Fatal("assign failed")
	}
	rec = httptest.NewRecorder()
	mux.ServeHTTP(rec, httptest.NewRequest("GET", "/users/u1/roles", nil))
	if rec.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", rec.Code)
	}
	var roles []Role
	json.NewDecoder(rec.Body).Decode(&roles)
	if len(roles) != 1 {
		t.Errorf("expected 1 role, got %d", len(roles))
	}
}

func TestUserRolesEmpty(t *testing.T) {
	mux := newTestMux()
	rec := httptest.NewRecorder()
	mux.ServeHTTP(rec, httptest.NewRequest("GET", "/users/u1/roles", nil))
	if rec.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", rec.Code)
	}
	var roles []Role
	json.NewDecoder(rec.Body).Decode(&roles)
	if roles == nil {
		t.Error("expected [] not null")
	}
	if len(roles) != 0 {
		t.Errorf("expected 0 roles, got %d", len(roles))
	}
}

func TestAuthzCheckAllowed(t *testing.T) {
	mux := newTestMux()
	role := createRole(t, mux, "reader", []string{"read"})
	assignBody := `{"roleId":"` + role.ID + `"}`
	rec := httptest.NewRecorder()
	mux.ServeHTTP(rec, httptest.NewRequest("POST", "/users/u1/roles", bytes.NewBufferString(assignBody)))

	checkBody := `{"userId":"u1","permission":"read"}`
	rec = httptest.NewRecorder()
	mux.ServeHTTP(rec, httptest.NewRequest("POST", "/authz/check", bytes.NewBufferString(checkBody)))
	if rec.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", rec.Code)
	}
	var res map[string]bool
	json.NewDecoder(rec.Body).Decode(&res)
	if !res["allowed"] {
		t.Error("expected allowed=true")
	}
}

func TestAuthzCheckDenied(t *testing.T) {
	mux := newTestMux()
	role := createRole(t, mux, "reader", []string{"read"})
	assignBody := `{"roleId":"` + role.ID + `"}`
	rec := httptest.NewRecorder()
	mux.ServeHTTP(rec, httptest.NewRequest("POST", "/users/u1/roles", bytes.NewBufferString(assignBody)))

	checkBody := `{"userId":"u1","permission":"delete"}`
	rec = httptest.NewRecorder()
	mux.ServeHTTP(rec, httptest.NewRequest("POST", "/authz/check", bytes.NewBufferString(checkBody)))
	if rec.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", rec.Code)
	}
	var res map[string]bool
	json.NewDecoder(rec.Body).Decode(&res)
	if res["allowed"] {
		t.Error("expected allowed=false")
	}
}

func TestMalformedJSON(t *testing.T) {
	mux := newTestMux()
	for _, tc := range []struct {
		method, path, body string
	}{
		{"POST", "/roles", "{bad}"},
		{"POST", "/users/u1/roles", "{bad}"},
		{"POST", "/authz/check", "{bad}"},
	} {
		rec := httptest.NewRecorder()
		mux.ServeHTTP(rec, httptest.NewRequest(tc.method, tc.path, bytes.NewBufferString(tc.body)))
		if rec.Code != http.StatusBadRequest {
			t.Errorf("%s %s: expected 400, got %d", tc.method, tc.path, rec.Code)
		}
	}
}
