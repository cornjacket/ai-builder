package handlers

import (
	"encoding/json"
	"net/http"

	"github.com/cornjacket/platform/internal/metrics/store"
)

type eventRequest struct {
	Type    string                 `json:"type"`
	UserID  string                 `json:"userId"`
	Payload map[string]interface{} `json:"payload"`
}

type eventResponse struct {
	ID      string                 `json:"id"`
	Type    string                 `json:"type"`
	UserID  string                 `json:"userId"`
	Payload map[string]interface{} `json:"payload"`
}

// Handler holds the store dependency.
type Handler struct {
	store store.Storer
}

// New constructs a Handler with the given Storer.
func New(s store.Storer) *Handler {
	return &Handler{store: s}
}

// PostEvents handles POST /events.
func (h *Handler) PostEvents(w http.ResponseWriter, r *http.Request) {
	var req eventRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "invalid JSON", http.StatusBadRequest)
		return
	}

	if req.Type != "click-mouse" && req.Type != "submit-form" {
		http.Error(w, "unknown type", http.StatusBadRequest)
		return
	}

	ev := h.store.Add(store.Event{
		Type:    req.Type,
		UserID:  req.UserID,
		Payload: req.Payload,
	})

	resp := eventResponse{
		ID:      ev.ID,
		Type:    ev.Type,
		UserID:  ev.UserID,
		Payload: ev.Payload,
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(resp)
}

// GetEvents handles GET /events.
func (h *Handler) GetEvents(w http.ResponseWriter, r *http.Request) {
	events := h.store.List()

	out := make([]eventResponse, len(events))
	for i, ev := range events {
		out[i] = eventResponse{
			ID:      ev.ID,
			Type:    ev.Type,
			UserID:  ev.UserID,
			Payload: ev.Payload,
		}
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(out)
}
