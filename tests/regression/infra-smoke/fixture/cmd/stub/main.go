// Stub HTTP server used by the infra-smoke test to validate the gold test
// framework without running the pipeline.
//
// Starts a single HTTP listener on the port given by the PORT environment
// variable (default 9099). Responds 200 OK to all requests.
package main

import (
	"fmt"
	"net/http"
	"os"
)

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "9099"
	}
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		fmt.Fprintln(w, "ok")
	})
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		fmt.Fprintf(os.Stderr, "stub: %v\n", err)
		os.Exit(1)
	}
}
