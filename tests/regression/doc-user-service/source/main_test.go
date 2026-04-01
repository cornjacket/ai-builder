// Package main tests the end-to-end HTTP behaviour of the user service.
//
// Purpose: Integration tests that exercise all six acceptance criteria via httptest.
// Tags: implementation, main
package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestUserServiceEndToEnd(t *testing.T) {
	srv := httptest.NewServer(newMux())
	defer srv.Close()

	var id string

	// 1. POST /users → 201 with non-empty id
	t.Run("POST /users creates user", func(t *testing.T) {
		body := bytes.NewBufferString(`{"name":"Alice","email":"a@b.com"}`)
		resp, err := http.Post(srv.URL+"/users", "application/json", body)
		if err != nil {
			t.Fatal(err)
		}
		defer resp.Body.Close()
		if resp.StatusCode != http.StatusCreated {
			t.Fatalf("want 201 got %d", resp.StatusCode)
		}
		var result struct {
			ID    string `json:"id"`
			Name  string `json:"name"`
			Email string `json:"email"`
		}
		if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
			t.Fatal(err)
		}
		if result.ID == "" {
			t.Fatal("expected non-empty id")
		}
		id = result.ID
	})

	// 2. GET /users/{id} with valid id → 200 correct record
	t.Run("GET /users/{id} returns correct record", func(t *testing.T) {
		resp, err := http.Get(srv.URL + "/users/" + id)
		if err != nil {
			t.Fatal(err)
		}
		defer resp.Body.Close()
		if resp.StatusCode != http.StatusOK {
			t.Fatalf("want 200 got %d", resp.StatusCode)
		}
		var result struct {
			ID    string `json:"id"`
			Name  string `json:"name"`
			Email string `json:"email"`
		}
		if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
			t.Fatal(err)
		}
		if result.Name != "Alice" || result.Email != "a@b.com" {
			t.Fatalf("unexpected record: %+v", result)
		}
	})

	// 3. GET /users/does-not-exist → 404
	t.Run("GET /users/{nonexistent} returns 404", func(t *testing.T) {
		resp, err := http.Get(srv.URL + "/users/does-not-exist")
		if err != nil {
			t.Fatal(err)
		}
		defer resp.Body.Close()
		if resp.StatusCode != http.StatusNotFound {
			t.Fatalf("want 404 got %d", resp.StatusCode)
		}
	})

	// 4. PUT /users/{id} → 200 updated record
	t.Run("PUT /users/{id} updates record", func(t *testing.T) {
		body := bytes.NewBufferString(`{"name":"Bob","email":"b@c.com"}`)
		req, err := http.NewRequest(http.MethodPut, srv.URL+"/users/"+id, body)
		if err != nil {
			t.Fatal(err)
		}
		req.Header.Set("Content-Type", "application/json")
		resp, err := http.DefaultClient.Do(req)
		if err != nil {
			t.Fatal(err)
		}
		defer resp.Body.Close()
		if resp.StatusCode != http.StatusOK {
			t.Fatalf("want 200 got %d", resp.StatusCode)
		}
		var result struct {
			ID    string `json:"id"`
			Name  string `json:"name"`
			Email string `json:"email"`
		}
		if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
			t.Fatal(err)
		}
		if result.Name != "Bob" || result.Email != "b@c.com" || result.ID != id {
			t.Fatalf("unexpected record: %+v", result)
		}
	})

	// 5. DELETE /users/{id} → 204
	t.Run("DELETE /users/{id} returns 204", func(t *testing.T) {
		req, err := http.NewRequest(http.MethodDelete, srv.URL+"/users/"+id, nil)
		if err != nil {
			t.Fatal(err)
		}
		resp, err := http.DefaultClient.Do(req)
		if err != nil {
			t.Fatal(err)
		}
		defer resp.Body.Close()
		if resp.StatusCode != http.StatusNoContent {
			t.Fatalf("want 204 got %d", resp.StatusCode)
		}
	})

	// 6. Second DELETE /users/{id} → 404
	t.Run("second DELETE /users/{id} returns 404", func(t *testing.T) {
		req, err := http.NewRequest(http.MethodDelete, srv.URL+"/users/"+id, nil)
		if err != nil {
			t.Fatal(err)
		}
		resp, err := http.DefaultClient.Do(req)
		if err != nil {
			t.Fatal(err)
		}
		defer resp.Body.Close()
		if resp.StatusCode != http.StatusNotFound {
			t.Fatalf("want 404 got %d", resp.StatusCode)
		}
	})
}
