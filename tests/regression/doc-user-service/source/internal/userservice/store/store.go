// Package store provides a thread-safe in-memory store for User records.
//
// Purpose: CRUD operations on User records backed by a map guarded by sync.RWMutex,
// with UUID generation for new record IDs.
//
// Tags: implementation, store
package store

import (
	"sync"

	"github.com/google/uuid"
)

// User represents a user record.
type User struct {
	ID    string
	Name  string
	Email string
}

// Store is a thread-safe in-memory store for User records.
type Store struct {
	mu   sync.RWMutex
	data map[string]User
}

// New returns an initialised *Store ready for use.
func New() *Store {
	return &Store{data: make(map[string]User)}
}

// Create ignores user.ID, assigns a fresh UUID, stores the record, and returns
// the populated User.
func (s *Store) Create(user User) User {
	s.mu.Lock()
	defer s.mu.Unlock()

	user.ID = uuid.NewString()
	s.data[user.ID] = user
	return user
}

// Get returns the User for id and true, or an empty User and false if not found.
func (s *Store) Get(id string) (User, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	u, ok := s.data[id]
	return u, ok
}

// Update replaces the stored record for id with user (preserving the original
// ID) and returns the updated User and true. Returns (User{}, false) if id is
// not found.
func (s *Store) Update(id string, user User) (User, bool) {
	s.mu.Lock()
	defer s.mu.Unlock()

	if _, ok := s.data[id]; !ok {
		return User{}, false
	}
	user.ID = id
	s.data[id] = user
	return user, true
}

// Delete removes the record for id and returns true, or false if not found.
func (s *Store) Delete(id string) bool {
	s.mu.Lock()
	defer s.mu.Unlock()

	if _, ok := s.data[id]; !ok {
		return false
	}
	delete(s.data, id)
	return true
}
