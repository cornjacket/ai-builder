package store

import (
	"sync"
	"testing"
)

func TestAdd_GeneratesUUID(t *testing.T) {
	s := New()
	e := s.Add(Event{Type: "click", UserID: "u1"})
	if e.ID == "" {
		t.Fatal("expected non-empty ID")
	}
}

func TestAdd_OverwritesCallerID(t *testing.T) {
	s := New()
	e := s.Add(Event{ID: "caller-id", Type: "click"})
	if e.ID == "caller-id" {
		t.Fatal("expected Add to overwrite caller-supplied ID")
	}
}

func TestAdd_PreservesFields(t *testing.T) {
	s := New()
	payload := map[string]interface{}{"key": "val"}
	e := s.Add(Event{Type: "purchase", UserID: "u2", Payload: payload})
	if e.Type != "purchase" {
		t.Errorf("Type: got %q, want %q", e.Type, "purchase")
	}
	if e.UserID != "u2" {
		t.Errorf("UserID: got %q, want %q", e.UserID, "u2")
	}
	if e.Payload["key"] != "val" {
		t.Errorf("Payload: got %v, want val", e.Payload["key"])
	}
}

func TestList_InsertionOrder(t *testing.T) {
	s := New()
	e1 := s.Add(Event{Type: "first"})
	e2 := s.Add(Event{Type: "second"})
	e3 := s.Add(Event{Type: "third"})

	list := s.List()
	if len(list) != 3 {
		t.Fatalf("expected 3 events, got %d", len(list))
	}
	if list[0].ID != e1.ID || list[1].ID != e2.ID || list[2].ID != e3.ID {
		t.Error("events not in insertion order")
	}
}

func TestList_CopySemantics(t *testing.T) {
	s := New()
	s.Add(Event{Type: "a"})

	list := s.List()
	// Appending to the returned slice must not affect subsequent List calls.
	list = append(list, Event{Type: "injected"})
	_ = list

	list2 := s.List()
	if len(list2) != 1 {
		t.Fatalf("expected 1 event after append to copy, got %d", len(list2))
	}
}

func TestRace_ConcurrentAddList(t *testing.T) {
	s := New()
	var wg sync.WaitGroup
	const goroutines = 50

	for i := 0; i < goroutines; i++ {
		wg.Add(2)
		go func() {
			defer wg.Done()
			s.Add(Event{Type: "t", UserID: "u"})
		}()
		go func() {
			defer wg.Done()
			_ = s.List()
		}()
	}
	wg.Wait()
}
