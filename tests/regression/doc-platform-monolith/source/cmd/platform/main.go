package main

import (
	"log"
	"net/http"

	"github.com/cornjacket/platform/internal/iam"
	"github.com/cornjacket/platform/internal/metrics"
)

func main() {
	metricsHandler := metrics.New()
	iamHandler := iam.New()

	go func() {
		log.Println("metrics: listening on :8081")
		if err := http.ListenAndServe(":8081", metricsHandler); err != nil {
			log.Fatalf("metrics: %v", err)
		}
	}()

	log.Println("iam: listening on :8082")
	if err := http.ListenAndServe(":8082", iamHandler); err != nil {
		log.Fatalf("iam: %v", err)
	}
}
