package metrics

import (
	"net/http"

	"github.com/cornjacket/platform/internal/metrics/handlers"
	"github.com/cornjacket/platform/internal/metrics/store"
)

// New wires the event store and HTTP handlers together and returns the
// resulting http.Handler. Routes: POST /events, GET /events.
func New() http.Handler {
	s := store.New()
	h := handlers.New(s)

	mux := http.NewServeMux()
	mux.HandleFunc("/events", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodPost:
			h.PostEvents(w, r)
		case http.MethodGet:
			h.GetEvents(w, r)
		default:
			http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		}
	})

	return mux
}
