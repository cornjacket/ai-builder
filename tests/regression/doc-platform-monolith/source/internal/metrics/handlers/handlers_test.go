package handlers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/cornjacket/platform/internal/metrics/store"
)

// stubStore is an in-memory stub satisfying store.Storer.
type stubStore struct {
	events []store.Event
	nextID int
}

func (s *stubStore) Add(e store.Event) store.Event {
	s.nextID++
	e.ID = "test-id"
	s.events = append(s.events, e)
	return e
}

func (s *stubStore) List() []store.Event {
	out := make([]store.Event, len(s.events))
	copy(out, s.events)
	return out
}

func newHandler() (*Handler, *stubStore) {
	st := &stubStore{}
	return New(st), st
}

func TestPostEvents(t *testing.T) {
	tests := []struct {
		name       string
		body       string
		wantStatus int
		wantType   string
		wantUserID string
	}{
		{
			name:       "click-mouse",
			body:       `{"type":"click-mouse","userId":"u1","payload":{"x":1}}`,
			wantStatus: http.StatusCreated,
			wantType:   "click-mouse",
			wantUserID: "u1",
		},
		{
			name:       "submit-form",
			body:       `{"type":"submit-form","userId":"u2","payload":{}}`,
			wantStatus: http.StatusCreated,
			wantType:   "submit-form",
			wantUserID: "u2",
		},
		{
			name:       "malformed JSON",
			body:       `{bad json`,
			wantStatus: http.StatusBadRequest,
		},
		{
			name:       "unknown type",
			body:       `{"type":"unknown","userId":"u1","payload":{}}`,
			wantStatus: http.StatusBadRequest,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			h, _ := newHandler()
			req := httptest.NewRequest(http.MethodPost, "/events", bytes.NewBufferString(tc.body))
			rec := httptest.NewRecorder()
			h.PostEvents(rec, req)

			if rec.Code != tc.wantStatus {
				t.Fatalf("status: got %d, want %d", rec.Code, tc.wantStatus)
			}
			if tc.wantStatus != http.StatusCreated {
				return
			}

			ct := rec.Header().Get("Content-Type")
			if ct != "application/json" {
				t.Errorf("Content-Type: got %q, want application/json", ct)
			}

			var resp eventResponse
			if err := json.NewDecoder(rec.Body).Decode(&resp); err != nil {
				t.Fatalf("decode response: %v", err)
			}
			if resp.ID == "" {
				t.Error("expected non-empty id")
			}
			if resp.Type != tc.wantType {
				t.Errorf("type: got %q, want %q", resp.Type, tc.wantType)
			}
			if resp.UserID != tc.wantUserID {
				t.Errorf("userId: got %q, want %q", resp.UserID, tc.wantUserID)
			}
		})
	}
}

func TestGetEvents(t *testing.T) {
	t.Run("empty store returns []", func(t *testing.T) {
		h, _ := newHandler()
		req := httptest.NewRequest(http.MethodGet, "/events", nil)
		rec := httptest.NewRecorder()
		h.GetEvents(rec, req)

		if rec.Code != http.StatusOK {
			t.Fatalf("status: got %d, want 200", rec.Code)
		}

		var out []eventResponse
		if err := json.NewDecoder(rec.Body).Decode(&out); err != nil {
			t.Fatalf("decode: %v", err)
		}
		if len(out) != 0 {
			t.Errorf("expected empty slice, got %d items", len(out))
		}
	})

	t.Run("returns all events after two POSTs", func(t *testing.T) {
		h, _ := newHandler()

		for _, body := range []string{
			`{"type":"click-mouse","userId":"u1","payload":{"x":1}}`,
			`{"type":"submit-form","userId":"u2","payload":{}}`,
		} {
			req := httptest.NewRequest(http.MethodPost, "/events", bytes.NewBufferString(body))
			rec := httptest.NewRecorder()
			h.PostEvents(rec, req)
			if rec.Code != http.StatusCreated {
				t.Fatalf("POST status: got %d", rec.Code)
			}
		}

		req := httptest.NewRequest(http.MethodGet, "/events", nil)
		rec := httptest.NewRecorder()
		h.GetEvents(rec, req)

		if rec.Code != http.StatusOK {
			t.Fatalf("GET status: got %d, want 200", rec.Code)
		}

		var out []eventResponse
		if err := json.NewDecoder(rec.Body).Decode(&out); err != nil {
			t.Fatalf("decode: %v", err)
		}
		if len(out) != 2 {
			t.Fatalf("expected 2 events, got %d", len(out))
		}
		if out[0].Type != "click-mouse" || out[0].UserID != "u1" {
			t.Errorf("event[0]: got %+v", out[0])
		}
		if out[1].Type != "submit-form" || out[1].UserID != "u2" {
			t.Errorf("event[1]: got %+v", out[1])
		}
	})
}
