package authz

import (
	"encoding/json"
	"net/http"
	"sync"

	"github.com/google/uuid"
)

type Role struct {
	ID          string   `json:"id"`
	Name        string   `json:"name"`
	Permissions []string `json:"permissions"`
}

type UserRoleAssignment struct {
	UserID string
	RoleID string
}

type store struct {
	mu          sync.RWMutex
	roles       map[string]Role
	assignments []UserRoleAssignment
}

func newStore() *store {
	return &store{
		roles:       make(map[string]Role),
		assignments: []UserRoleAssignment{},
	}
}

func (s *store) addRole(name string, permissions []string) Role {
	if permissions == nil {
		permissions = []string{}
	}
	r := Role{
		ID:          uuid.New().String(),
		Name:        name,
		Permissions: permissions,
	}
	s.mu.Lock()
	s.roles[r.ID] = r
	s.mu.Unlock()
	return r
}

func (s *store) listRoles() []Role {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]Role, 0, len(s.roles))
	for _, r := range s.roles {
		out = append(out, r)
	}
	return out
}

func (s *store) getRole(id string) (Role, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	r, ok := s.roles[id]
	return r, ok
}

// assignRole returns false if roleID is unknown.
func (s *store) assignRole(userID, roleID string) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.roles[roleID]; !ok {
		return false
	}
	s.assignments = append(s.assignments, UserRoleAssignment{UserID: userID, RoleID: roleID})
	return true
}

func (s *store) rolesForUser(userID string) []Role {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := []Role{}
	for _, a := range s.assignments {
		if a.UserID == userID {
			if r, ok := s.roles[a.RoleID]; ok {
				out = append(out, r)
			}
		}
	}
	return out
}

func (s *store) hasPermission(userID, permission string) bool {
	s.mu.RLock()
	defer s.mu.RUnlock()
	for _, a := range s.assignments {
		if a.UserID != userID {
			continue
		}
		r, ok := s.roles[a.RoleID]
		if !ok {
			continue
		}
		for _, p := range r.Permissions {
			if p == permission {
				return true
			}
		}
	}
	return false
}

type Handler struct{ s *store }

func New() *Handler {
	return &Handler{s: newStore()}
}

func (h *Handler) RegisterRoutes(mux *http.ServeMux) {
	mux.HandleFunc("POST /roles", h.createRole)
	mux.HandleFunc("GET /roles", h.listRoles)
	mux.HandleFunc("POST /users/{id}/roles", h.assignRole)
	mux.HandleFunc("GET /users/{id}/roles", h.userRoles)
	mux.HandleFunc("POST /authz/check", h.checkPermission)
}

func (h *Handler) createRole(w http.ResponseWriter, r *http.Request) {
	var req struct {
		Name        string   `json:"name"`
		Permissions []string `json:"permissions"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "bad request", http.StatusBadRequest)
		return
	}
	role := h.s.addRole(req.Name, req.Permissions)
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(role)
}

func (h *Handler) listRoles(w http.ResponseWriter, r *http.Request) {
	roles := h.s.listRoles()
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(roles)
}

func (h *Handler) assignRole(w http.ResponseWriter, r *http.Request) {
	userID := r.PathValue("id")
	var req struct {
		RoleID string `json:"roleId"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "bad request", http.StatusBadRequest)
		return
	}
	if !h.s.assignRole(userID, req.RoleID) {
		http.Error(w, "role not found", http.StatusNotFound)
		return
	}
	w.WriteHeader(http.StatusCreated)
}

func (h *Handler) userRoles(w http.ResponseWriter, r *http.Request) {
	userID := r.PathValue("id")
	roles := h.s.rolesForUser(userID)
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(roles)
}

func (h *Handler) checkPermission(w http.ResponseWriter, r *http.Request) {
	var req struct {
		UserID     string `json:"userId"`
		Permission string `json:"permission"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "bad request", http.StatusBadRequest)
		return
	}
	allowed := h.s.hasPermission(req.UserID, req.Permission)
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]bool{"allowed": allowed})
}
