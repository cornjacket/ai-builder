// Package main is the entry point for the user service.
//
// Purpose: Wire store and handlers into a ServeMux and start net/http on port 8080.
// Tags: implementation, main
package main

import (
	"log"
	"net/http"

	"github.com/cornjacket/ai-builder/sandbox/regressions/user-service/output/internal/userservice/handlers"
	"github.com/cornjacket/ai-builder/sandbox/regressions/user-service/output/internal/userservice/store"
)

func newMux() *http.ServeMux {
	s := store.New()
	h := handlers.New(s)
	mux := http.NewServeMux()
	h.RegisterRoutes(mux)
	return mux
}

func main() {
	log.Fatal(http.ListenAndServe(":8080", newMux()))
}
