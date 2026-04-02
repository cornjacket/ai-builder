// Package handlers provides HTTP CRUD handlers for the user service.
//
// Purpose: httptest-based tests covering every status-code path for the four
// CRUD handlers, using a stub in-memory store.
//
// Tags: test, handlers
package handlers

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/cornjacket/ai-builder/sandbox/regressions/user-service/output/internal/userservice/store"
)

// stubStore is an in-memory Store implementation for testing.
type stubStore struct {
	data   map[string]store.User
	nextID int
}

func newStubStore() *stubStore {
	return &stubStore{data: make(map[string]store.User)}
}

func (s *stubStore) Create(user store.User) store.User {
	s.nextID++
	user.ID = string(rune('a' + s.nextID - 1))
	s.data[user.ID] = user
	return user
}

func (s *stubStore) Get(id string) (store.User, bool) {
	u, ok := s.data[id]
	return u, ok
}

func (s *stubStore) Update(id string, user store.User) (store.User, bool) {
	if _, ok := s.data[id]; !ok {
		return store.User{}, false
	}
	user.ID = id
	s.data[id] = user
	return user, true
}

func (s *stubStore) Delete(id string) bool {
	if _, ok := s.data[id]; !ok {
		return false
	}
	delete(s.data, id)
	return true
}

func setup() (*Handler, *http.ServeMux) {
	s := newStubStore()
	h := New(s)
	mux := http.NewServeMux()
	h.RegisterRoutes(mux)
	return h, mux
}

func TestCreateUser_Success(t *testing.T) {
	_, mux := setup()
	body := `{"name":"Alice","email":"a@example.com"}`
	req := httptest.NewRequest(http.MethodPost, "/users", strings.NewReader(body))
	w := httptest.NewRecorder()
	mux.ServeHTTP(w, req)

	if w.Code != http.StatusCreated {
		t.Fatalf("expected 201, got %d", w.Code)
	}
	if ct := w.Header().Get("Content-Type"); ct != "application/json" {
		t.Fatalf("expected Content-Type application/json, got %q", ct)
	}
	var resp userJSON
	if err := json.NewDecoder(w.Body).Decode(&resp); err != nil {
		t.Fatalf("decode response: %v", err)
	}
	if resp.ID == "" {
		t.Error("expected non-empty id")
	}
	if resp.Name != "Alice" {
		t.Errorf("expected name Alice, got %q", resp.Name)
	}
	if resp.Email != "a@example.com" {
		t.Errorf("expected email a@example.com, got %q", resp.Email)
	}
}

func TestCreateUser_BadJSON(t *testing.T) {
	_, mux := setup()
	req := httptest.NewRequest(http.MethodPost, "/users", strings.NewReader("{bad"))
	w := httptest.NewRecorder()
	mux.ServeHTTP(w, req)

	if w.Code != http.StatusBadRequest {
		t.Fatalf("expected 400, got %d", w.Code)
	}
	if ct := w.Header().Get("Content-Type"); ct != "application/json" {
		t.Fatalf("expected Content-Type application/json, got %q", ct)
	}
	var resp map[string]string
	if err := json.NewDecoder(w.Body).Decode(&resp); err != nil {
		t.Fatalf("decode response: %v", err)
	}
	if resp["error"] == "" {
		t.Error("expected non-empty error field")
	}
}

func TestGetUser_Found(t *testing.T) {
	h, mux := setup()
	// seed the store via the handler's store
	u := h.store.Create(store.User{Name: "Bob", Email: "b@example.com"})

	req := httptest.NewRequest(http.MethodGet, "/users/"+u.ID, nil)
	w := httptest.NewRecorder()
	mux.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", w.Code)
	}
	if ct := w.Header().Get("Content-Type"); ct != "application/json" {
		t.Fatalf("expected Content-Type application/json, got %q", ct)
	}
	var resp userJSON
	if err := json.NewDecoder(w.Body).Decode(&resp); err != nil {
		t.Fatalf("decode response: %v", err)
	}
	if resp.ID != u.ID {
		t.Errorf("expected id %q, got %q", u.ID, resp.ID)
	}
	if resp.Name != "Bob" {
		t.Errorf("expected name Bob, got %q", resp.Name)
	}
}

func TestGetUser_NotFound(t *testing.T) {
	_, mux := setup()
	req := httptest.NewRequest(http.MethodGet, "/users/nonexistent", nil)
	w := httptest.NewRecorder()
	mux.ServeHTTP(w, req)

	if w.Code != http.StatusNotFound {
		t.Fatalf("expected 404, got %d", w.Code)
	}
	if ct := w.Header().Get("Content-Type"); ct != "application/json" {
		t.Fatalf("expected Content-Type application/json, got %q", ct)
	}
	var resp map[string]string
	if err := json.NewDecoder(w.Body).Decode(&resp); err != nil {
		t.Fatalf("decode response: %v", err)
	}
	if resp["error"] != "not found" {
		t.Errorf("expected error 'not found', got %q", resp["error"])
	}
}

func TestUpdateUser_Success(t *testing.T) {
	h, mux := setup()
	u := h.store.Create(store.User{Name: "Carol", Email: "c@example.com"})

	body := `{"name":"Carol Updated","email":"cu@example.com"}`
	req := httptest.NewRequest(http.MethodPut, "/users/"+u.ID, strings.NewReader(body))
	w := httptest.NewRecorder()
	mux.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", w.Code)
	}
	if ct := w.Header().Get("Content-Type"); ct != "application/json" {
		t.Fatalf("expected Content-Type application/json, got %q", ct)
	}
	var resp userJSON
	if err := json.NewDecoder(w.Body).Decode(&resp); err != nil {
		t.Fatalf("decode response: %v", err)
	}
	if resp.ID != u.ID {
		t.Errorf("expected id %q (unchanged), got %q", u.ID, resp.ID)
	}
	if resp.Name != "Carol Updated" {
		t.Errorf("expected updated name, got %q", resp.Name)
	}
}

func TestUpdateUser_NotFound(t *testing.T) {
	_, mux := setup()
	body := `{"name":"X","email":"x@example.com"}`
	req := httptest.NewRequest(http.MethodPut, "/users/nonexistent", strings.NewReader(body))
	w := httptest.NewRecorder()
	mux.ServeHTTP(w, req)

	if w.Code != http.StatusNotFound {
		t.Fatalf("expected 404, got %d", w.Code)
	}
	if ct := w.Header().Get("Content-Type"); ct != "application/json" {
		t.Fatalf("expected Content-Type application/json, got %q", ct)
	}
	var resp map[string]string
	if err := json.NewDecoder(w.Body).Decode(&resp); err != nil {
		t.Fatalf("decode response: %v", err)
	}
	if resp["error"] != "not found" {
		t.Errorf("expected error 'not found', got %q", resp["error"])
	}
}

func TestUpdateUser_BadJSON(t *testing.T) {
	_, mux := setup()
	req := httptest.NewRequest(http.MethodPut, "/users/anyid", strings.NewReader("{bad"))
	w := httptest.NewRecorder()
	mux.ServeHTTP(w, req)

	if w.Code != http.StatusBadRequest {
		t.Fatalf("expected 400, got %d", w.Code)
	}
	if ct := w.Header().Get("Content-Type"); ct != "application/json" {
		t.Fatalf("expected Content-Type application/json, got %q", ct)
	}
	var resp map[string]string
	if err := json.NewDecoder(w.Body).Decode(&resp); err != nil {
		t.Fatalf("decode response: %v", err)
	}
	if resp["error"] == "" {
		t.Error("expected non-empty error field")
	}
}

func TestDeleteUser_Success(t *testing.T) {
	h, mux := setup()
	u := h.store.Create(store.User{Name: "Dave", Email: "d@example.com"})

	req := httptest.NewRequest(http.MethodDelete, "/users/"+u.ID, nil)
	w := httptest.NewRecorder()
	mux.ServeHTTP(w, req)

	if w.Code != http.StatusNoContent {
		t.Fatalf("expected 204, got %d", w.Code)
	}
	if w.Body.Len() != 0 {
		t.Errorf("expected empty body, got %q", w.Body.String())
	}
}

func TestDeleteUser_NotFound(t *testing.T) {
	_, mux := setup()
	req := httptest.NewRequest(http.MethodDelete, "/users/nonexistent", nil)
	w := httptest.NewRecorder()
	mux.ServeHTTP(w, req)

	if w.Code != http.StatusNotFound {
		t.Fatalf("expected 404, got %d", w.Code)
	}
	if ct := w.Header().Get("Content-Type"); ct != "application/json" {
		t.Fatalf("expected Content-Type application/json, got %q", ct)
	}
	var resp map[string]string
	if err := json.NewDecoder(w.Body).Decode(&resp); err != nil {
		t.Fatalf("decode response: %v", err)
	}
	if resp["error"] != "not found" {
		t.Errorf("expected error 'not found', got %q", resp["error"])
	}
}
