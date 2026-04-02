package iam

import (
	"net/http"

	"github.com/cornjacket/platform/internal/iam/authz"
	"github.com/cornjacket/platform/internal/iam/lifecycle"
)

// New instantiates lifecycle and authz handlers, registers all ten routes on a
// single ServeMux, and returns the mux as an http.Handler. The caller binds it
// to :8082.
func New() http.Handler {
	mux := http.NewServeMux()
	lifecycle.New().RegisterRoutes(mux)
	authz.New().RegisterRoutes(mux)
	return mux
}
