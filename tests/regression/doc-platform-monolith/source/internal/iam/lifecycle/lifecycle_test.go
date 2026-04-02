package lifecycle

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

func TestCreateUser(t *testing.T) {
	mux := newTestMux()
	body := `{"username":"alice","password":"secret"}`
	w := httptest.NewRecorder()
	mux.ServeHTTP(w, httptest.NewRequest(http.MethodPost, "/users", bytes.NewBufferString(body)))
	if w.Code != http.StatusCreated {
		t.Fatalf("expected 201, got %d", w.Code)
	}
	var resp map[string]string
	if err := json.NewDecoder(w.Body).Decode(&resp); err != nil {
		t.Fatal(err)
	}
	if resp["id"] == "" {
		t.Error("expected non-empty id")
	}
	if resp["username"] != "alice" {
		t.Errorf("expected username alice, got %s", resp["username"])
	}
}

func TestGetUser(t *testing.T) {
	mux := newTestMux()
	id := createUser(t, mux, "alice", "secret")

	w := httptest.NewRecorder()
	mux.ServeHTTP(w, httptest.NewRequest(http.MethodGet, "/users/"+id, nil))
	if w.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", w.Code)
	}
	var resp map[string]string
	json.NewDecoder(w.Body).Decode(&resp)
	if resp["id"] != id {
		t.Errorf("id mismatch: got %s", resp["id"])
	}
	if resp["username"] != "alice" {
		t.Errorf("username mismatch: got %s", resp["username"])
	}
}

func TestGetUserNotFound(t *testing.T) {
	mux := newTestMux()
	w := httptest.NewRecorder()
	mux.ServeHTTP(w, httptest.NewRequest(http.MethodGet, "/users/nonexistent", nil))
	if w.Code != http.StatusNotFound {
		t.Fatalf("expected 404, got %d", w.Code)
	}
}

func TestDeleteUser(t *testing.T) {
	mux := newTestMux()
	id := createUser(t, mux, "bob", "pass")

	w := httptest.NewRecorder()
	mux.ServeHTTP(w, httptest.NewRequest(http.MethodDelete, "/users/"+id, nil))
	if w.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", w.Code)
	}
}

func TestDeleteUserNotFound(t *testing.T) {
	mux := newTestMux()
	w := httptest.NewRecorder()
	mux.ServeHTTP(w, httptest.NewRequest(http.MethodDelete, "/users/nonexistent", nil))
	if w.Code != http.StatusNotFound {
		t.Fatalf("expected 404, got %d", w.Code)
	}
}

func TestLogin(t *testing.T) {
	mux := newTestMux()
	createUser(t, mux, "alice", "secret")

	token := loginUser(t, mux, "alice", "secret")
	if token == "" {
		t.Error("expected non-empty token")
	}
}

func TestLoginWrongPassword(t *testing.T) {
	mux := newTestMux()
	createUser(t, mux, "alice", "secret")

	w := httptest.NewRecorder()
	mux.ServeHTTP(w, httptest.NewRequest(http.MethodPost, "/auth/login",
		bytes.NewBufferString(`{"username":"alice","password":"wrong"}`)))
	if w.Code != http.StatusUnauthorized {
		t.Fatalf("expected 401, got %d", w.Code)
	}
}

func TestLoginUnknownUser(t *testing.T) {
	mux := newTestMux()
	w := httptest.NewRecorder()
	mux.ServeHTTP(w, httptest.NewRequest(http.MethodPost, "/auth/login",
		bytes.NewBufferString(`{"username":"nobody","password":"x"}`)))
	if w.Code != http.StatusUnauthorized {
		t.Fatalf("expected 401, got %d", w.Code)
	}
}

func TestLogout(t *testing.T) {
	mux := newTestMux()
	createUser(t, mux, "alice", "secret")
	token := loginUser(t, mux, "alice", "secret")

	w := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/auth/logout", nil)
	req.Header.Set("Authorization", "Bearer "+token)
	mux.ServeHTTP(w, req)
	if w.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", w.Code)
	}
}

func TestLogoutMissingToken(t *testing.T) {
	mux := newTestMux()
	w := httptest.NewRecorder()
	mux.ServeHTTP(w, httptest.NewRequest(http.MethodPost, "/auth/logout", nil))
	if w.Code != http.StatusUnauthorized {
		t.Fatalf("expected 401, got %d", w.Code)
	}
}

func TestLogoutUnknownToken(t *testing.T) {
	mux := newTestMux()
	w := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/auth/logout", nil)
	req.Header.Set("Authorization", "Bearer unknowntoken")
	mux.ServeHTTP(w, req)
	if w.Code != http.StatusUnauthorized {
		t.Fatalf("expected 401, got %d", w.Code)
	}
}

func TestLogoutTokenInvalidatedAfterUse(t *testing.T) {
	mux := newTestMux()
	createUser(t, mux, "alice", "secret")
	token := loginUser(t, mux, "alice", "secret")

	// First logout succeeds.
	w := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/auth/logout", nil)
	req.Header.Set("Authorization", "Bearer "+token)
	mux.ServeHTTP(w, req)
	if w.Code != http.StatusOK {
		t.Fatalf("first logout: expected 200, got %d", w.Code)
	}

	// Second logout with same token must fail.
	w2 := httptest.NewRecorder()
	req2 := httptest.NewRequest(http.MethodPost, "/auth/logout", nil)
	req2.Header.Set("Authorization", "Bearer "+token)
	mux.ServeHTTP(w2, req2)
	if w2.Code != http.StatusUnauthorized {
		t.Fatalf("second logout: expected 401, got %d", w2.Code)
	}
}

func TestDuplicateUsername(t *testing.T) {
	mux := newTestMux()
	createUser(t, mux, "alice", "secret")

	w := httptest.NewRecorder()
	mux.ServeHTTP(w, httptest.NewRequest(http.MethodPost, "/users",
		bytes.NewBufferString(`{"username":"alice","password":"other"}`)))
	if w.Code != http.StatusConflict {
		t.Fatalf("expected 409, got %d", w.Code)
	}
}

// helpers

func createUser(t *testing.T, mux *http.ServeMux, username, password string) string {
	t.Helper()
	body, _ := json.Marshal(map[string]string{"username": username, "password": password})
	w := httptest.NewRecorder()
	mux.ServeHTTP(w, httptest.NewRequest(http.MethodPost, "/users", bytes.NewBuffer(body)))
	if w.Code != http.StatusCreated {
		t.Fatalf("createUser: expected 201, got %d: %s", w.Code, w.Body.String())
	}
	var resp map[string]string
	json.NewDecoder(w.Body).Decode(&resp)
	return resp["id"]
}

func loginUser(t *testing.T, mux *http.ServeMux, username, password string) string {
	t.Helper()
	body, _ := json.Marshal(map[string]string{"username": username, "password": password})
	w := httptest.NewRecorder()
	mux.ServeHTTP(w, httptest.NewRequest(http.MethodPost, "/auth/login", bytes.NewBuffer(body)))
	if w.Code != http.StatusOK {
		t.Fatalf("loginUser: expected 200, got %d: %s", w.Code, w.Body.String())
	}
	var resp map[string]string
	json.NewDecoder(w.Body).Decode(&resp)
	return resp["token"]
}
