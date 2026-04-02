package lifecycle

import (
	"encoding/json"
	"net/http"
	"strings"
	"sync"

	"github.com/google/uuid"
	"golang.org/x/crypto/bcrypt"
)

// User represents a registered user.
type User struct {
	ID           string
	Username     string
	PasswordHash string
}

// Token represents an active session token.
type Token struct {
	Token  string
	UserID string
}

// Store holds all in-memory state behind a single RWMutex.
type Store struct {
	mu     sync.RWMutex
	users  map[string]User   // id → User
	byName map[string]string // username → id
	tokens map[string]Token  // token → Token
}

func newStore() *Store {
	return &Store{
		users:  make(map[string]User),
		byName: make(map[string]string),
		tokens: make(map[string]Token),
	}
}

func (s *Store) addUser(username, passwordHash string) (User, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, exists := s.byName[username]; exists {
		return User{}, errUsernameTaken
	}
	u := User{ID: uuid.NewString(), Username: username, PasswordHash: passwordHash}
	s.users[u.ID] = u
	s.byName[username] = u.ID
	return u, nil
}

func (s *Store) getUser(id string) (User, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	u, ok := s.users[id]
	return u, ok
}

func (s *Store) getUserByName(username string) (User, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	id, ok := s.byName[username]
	if !ok {
		return User{}, false
	}
	u, ok := s.users[id]
	return u, ok
}

func (s *Store) deleteUser(id string) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	u, ok := s.users[id]
	if !ok {
		return false
	}
	delete(s.byName, u.Username)
	delete(s.users, id)
	return true
}

func (s *Store) addToken(userID string) Token {
	t := Token{Token: uuid.NewString(), UserID: userID}
	s.mu.Lock()
	defer s.mu.Unlock()
	s.tokens[t.Token] = t
	return t
}

func (s *Store) getToken(token string) (Token, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	t, ok := s.tokens[token]
	return t, ok
}

func (s *Store) deleteToken(token string) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	_, ok := s.tokens[token]
	if !ok {
		return false
	}
	delete(s.tokens, token)
	return true
}

// errUsernameTaken is returned by addUser when the username is already registered.
var errUsernameTaken = errDuplicate("username already taken")

type errDuplicate string

func (e errDuplicate) Error() string { return string(e) }

// Handler exposes the lifecycle HTTP endpoints.
type Handler struct {
	store *Store
}

// New constructs a Handler with a fresh in-memory Store.
func New() *Handler {
	return &Handler{store: newStore()}
}

// RegisterRoutes registers lifecycle endpoints onto mux.
func (h *Handler) RegisterRoutes(mux *http.ServeMux) {
	mux.HandleFunc("/users", h.handleUsers)
	mux.HandleFunc("/users/", h.handleUserByID)
	mux.HandleFunc("/auth/login", h.handleLogin)
	mux.HandleFunc("/auth/logout", h.handleLogout)
}

// POST /users
func (h *Handler) handleUsers(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}
	var req struct {
		Username string `json:"username"`
		Password string `json:"password"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "bad request", http.StatusBadRequest)
		return
	}
	hash, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
	if err != nil {
		http.Error(w, "internal error", http.StatusInternalServerError)
		return
	}
	u, err := h.store.addUser(req.Username, string(hash))
	if err != nil {
		http.Error(w, err.Error(), http.StatusConflict)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(map[string]string{"id": u.ID, "username": u.Username})
}

// GET /users/{id}, DELETE /users/{id}
func (h *Handler) handleUserByID(w http.ResponseWriter, r *http.Request) {
	id := strings.TrimPrefix(r.URL.Path, "/users/")
	if id == "" {
		http.NotFound(w, r)
		return
	}
	switch r.Method {
	case http.MethodGet:
		u, ok := h.store.getUser(id)
		if !ok {
			http.NotFound(w, r)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]string{"id": u.ID, "username": u.Username})
	case http.MethodDelete:
		if !h.store.deleteUser(id) {
			http.NotFound(w, r)
			return
		}
		w.WriteHeader(http.StatusOK)
	default:
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
	}
}

// POST /auth/login
func (h *Handler) handleLogin(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}
	var req struct {
		Username string `json:"username"`
		Password string `json:"password"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "bad request", http.StatusBadRequest)
		return
	}
	u, ok := h.store.getUserByName(req.Username)
	if !ok {
		http.Error(w, "unauthorized", http.StatusUnauthorized)
		return
	}
	if err := bcrypt.CompareHashAndPassword([]byte(u.PasswordHash), []byte(req.Password)); err != nil {
		http.Error(w, "unauthorized", http.StatusUnauthorized)
		return
	}
	t := h.store.addToken(u.ID)
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"token": t.Token})
}

// POST /auth/logout
func (h *Handler) handleLogout(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}
	auth := r.Header.Get("Authorization")
	token := strings.TrimPrefix(auth, "Bearer ")
	if token == "" || token == auth {
		http.Error(w, "unauthorized", http.StatusUnauthorized)
		return
	}
	if !h.store.deleteToken(token) {
		http.Error(w, "unauthorized", http.StatusUnauthorized)
		return
	}
	w.WriteHeader(http.StatusOK)
}
