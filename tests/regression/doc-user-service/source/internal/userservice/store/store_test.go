// Package store provides a thread-safe in-memory store for User records.
//
// Purpose: Unit tests for the Store type covering sequential lifecycle,
// not-found paths, and concurrent Create+Get under -race.
//
// Tags: test, store
package store

import (
	"sync"
	"testing"
)

// TestSequentialLifecycle covers Create → Get → Update → Delete for a single record.
func TestSequentialLifecycle(t *testing.T) {
	s := New()

	// Create
	input := User{ID: "ignored", Name: "Alice", Email: "alice@example.com"}
	created := s.Create(input)
	if created.ID == "" {
		t.Fatal("Create: ID must not be empty")
	}
	if created.ID == input.ID {
		t.Errorf("Create: ID must not equal caller-supplied ID %q", input.ID)
	}
	if created.Name != input.Name || created.Email != input.Email {
		t.Errorf("Create: unexpected Name/Email: got %+v", created)
	}

	// Get hit
	got, ok := s.Get(created.ID)
	if !ok {
		t.Fatal("Get: expected true for existing record")
	}
	if got != created {
		t.Errorf("Get: expected %+v, got %+v", created, got)
	}

	// Update hit
	updated, ok := s.Update(created.ID, User{Name: "Bob", Email: "bob@example.com"})
	if !ok {
		t.Fatal("Update: expected true for existing record")
	}
	if updated.ID != created.ID {
		t.Errorf("Update: ID must be preserved; want %q, got %q", created.ID, updated.ID)
	}
	if updated.Name != "Bob" || updated.Email != "bob@example.com" {
		t.Errorf("Update: unexpected fields: %+v", updated)
	}

	// Get reflects update
	got2, ok := s.Get(created.ID)
	if !ok {
		t.Fatal("Get after Update: expected true")
	}
	if got2 != updated {
		t.Errorf("Get after Update: expected %+v, got %+v", updated, got2)
	}

	// Delete hit
	if !s.Delete(created.ID) {
		t.Fatal("Delete: expected true for existing record")
	}

	// Get after Delete
	_, ok = s.Get(created.ID)
	if ok {
		t.Fatal("Get after Delete: expected false")
	}
}

func TestUpdateNotFound(t *testing.T) {
	s := New()
	u, ok := s.Update("no-such-id", User{Name: "X"})
	if ok {
		t.Fatal("Update on unknown ID: expected false")
	}
	if u != (User{}) {
		t.Errorf("Update on unknown ID: expected zero User, got %+v", u)
	}
}

func TestDeleteNotFound(t *testing.T) {
	s := New()
	if s.Delete("no-such-id") {
		t.Fatal("Delete on unknown ID: expected false")
	}
}

func TestGetNotFound(t *testing.T) {
	s := New()
	u, ok := s.Get("no-such-id")
	if ok {
		t.Fatal("Get on unknown ID: expected false")
	}
	if u != (User{}) {
		t.Errorf("Get on unknown ID: expected zero User, got %+v", u)
	}
}

// TestConcurrentCreate verifies that 200 concurrent Creates produce 200 distinct
// IDs with no data races (run with go test -race).
func TestConcurrentCreate(t *testing.T) {
	const goroutines = 2
	const perGoroutine = 100

	s := New()
	var wg sync.WaitGroup
	ids := make(chan string, goroutines*perGoroutine)

	for g := 0; g < goroutines; g++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for i := 0; i < perGoroutine; i++ {
				u := s.Create(User{Name: "user", Email: "u@example.com"})
				ids <- u.ID
			}
		}()
	}

	wg.Wait()
	close(ids)

	seen := make(map[string]struct{})
	for id := range ids {
		if _, dup := seen[id]; dup {
			t.Errorf("duplicate ID: %q", id)
		}
		seen[id] = struct{}{}
	}
	if len(seen) != goroutines*perGoroutine {
		t.Errorf("expected %d distinct IDs, got %d", goroutines*perGoroutine, len(seen))
	}
}
