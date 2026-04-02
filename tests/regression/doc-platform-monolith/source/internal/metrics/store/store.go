package store

import (
	"sync"

	"github.com/google/uuid"
)

// Event represents a metrics event.
type Event struct {
	ID      string
	Type    string
	UserID  string
	Payload map[string]interface{}
}

// Storer is the interface for the event store.
type Storer interface {
	Add(e Event) Event
	List() []Event
}

// Compile-time assertion that *Store satisfies Storer.
var _ Storer = (*Store)(nil)

// Store is an in-memory, concurrency-safe event store.
type Store struct {
	mu     sync.RWMutex
	events []Event
}

// New returns a new Store.
func New() *Store {
	return &Store{}
}

// Add assigns a UUID to the event, stores it, and returns the stored event.
func (s *Store) Add(e Event) Event {
	e.ID = uuid.NewString()
	s.mu.Lock()
	s.events = append(s.events, e)
	s.mu.Unlock()
	return e
}

// List returns a shallow copy of all stored events in insertion order.
func (s *Store) List() []Event {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]Event, len(s.events))
	copy(out, s.events)
	return out
}
