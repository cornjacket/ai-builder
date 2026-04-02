// Package handlers provides HTTP CRUD handlers for the user service.
//
// Purpose: HTTP handler wiring for POST/GET/PUT/DELETE /users routes,
// decoding JSON request bodies and encoding JSON responses via a Store interface.
//
// Tags: implementation, handlers
package handlers

import (
	"encoding/json"
	"net/http"

	"github.com/cornjacket/ai-builder/sandbox/regressions/user-service/output/internal/userservice/store"
)

// Store is the interface that the store package's *store.Store satisfies.
type Store interface {
	Create(user store.User) store.User
	Get(id string) (store.User, bool)
	Update(id string, user store.User) (store.User, bool)
	Delete(id string) bool
}

// userJSON is used for all JSON responses.
type userJSON struct {
	ID    string `json:"id"`
	Name  string `json:"name"`
	Email string `json:"email"`
}

// userInput is the request body for POST and PUT (ID is never accepted from the caller).
type userInput struct {
	Name  string `json:"name"`
	Email string `json:"email"`
}

// Handler holds the Store and exposes RegisterRoutes.
type Handler struct {
	store Store
}

// New returns a *Handler backed by s.
func New(s Store) *Handler {
	return &Handler{store: s}
}

// RegisterRoutes wires the four CRUD routes onto mux using Go 1.22 patterns.
func (h *Handler) RegisterRoutes(mux *http.ServeMux) {
	mux.HandleFunc("POST /users", h.createUser)
	mux.HandleFunc("GET /users/{id}", h.getUser)
	mux.HandleFunc("PUT /users/{id}", h.updateUser)
	mux.HandleFunc("DELETE /users/{id}", h.deleteUser)
}

func (h *Handler) createUser(w http.ResponseWriter, r *http.Request) {
	var input userInput
	if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
		writeError(w, http.StatusBadRequest, err.Error())
		return
	}
	u := h.store.Create(store.User{Name: input.Name, Email: input.Email})
	writeJSON(w, http.StatusCreated, userJSON{ID: u.ID, Name: u.Name, Email: u.Email})
}

func (h *Handler) getUser(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	u, ok := h.store.Get(id)
	if !ok {
		writeError(w, http.StatusNotFound, "not found")
		return
	}
	writeJSON(w, http.StatusOK, userJSON{ID: u.ID, Name: u.Name, Email: u.Email})
}

func (h *Handler) updateUser(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	var input userInput
	if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
		writeError(w, http.StatusBadRequest, err.Error())
		return
	}
	u, ok := h.store.Update(id, store.User{Name: input.Name, Email: input.Email})
	if !ok {
		writeError(w, http.StatusNotFound, "not found")
		return
	}
	writeJSON(w, http.StatusOK, userJSON{ID: u.ID, Name: u.Name, Email: u.Email})
}

func (h *Handler) deleteUser(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	if !h.store.Delete(id) {
		writeError(w, http.StatusNotFound, "not found")
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

// writeJSON sets Content-Type, writes the status code, and encodes v as JSON.
func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(v) //nolint:errcheck
}

// writeError writes a JSON error response with the given status and message.
func writeError(w http.ResponseWriter, status int, msg string) {
	writeJSON(w, status, struct {
		Error string `json:"error"`
	}{msg})
}
