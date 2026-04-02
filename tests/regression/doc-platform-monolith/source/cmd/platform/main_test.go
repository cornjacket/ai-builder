package main_test

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/cornjacket/platform/internal/iam"
	"github.com/cornjacket/platform/internal/metrics"
)

func metricsServer(t *testing.T) *httptest.Server {
	t.Helper()
	ts := httptest.NewServer(metrics.New())
	t.Cleanup(ts.Close)
	return ts
}

func iamServer(t *testing.T) *httptest.Server {
	t.Helper()
	ts := httptest.NewServer(iam.New())
	t.Cleanup(ts.Close)
	return ts
}

// postJSON issues a POST with an optional JSON body and optional extra headers.
// body == nil sends an empty body.
func postJSON(t *testing.T, url string, body interface{}, headers map[string]string) *http.Response {
	t.Helper()
	var r io.Reader
	if body != nil {
		b, err := json.Marshal(body)
		if err != nil {
			t.Fatalf("marshal body: %v", err)
		}
		r = bytes.NewReader(b)
	}
	req, err := http.NewRequest(http.MethodPost, url, r)
	if err != nil {
		t.Fatalf("new request: %v", err)
	}
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}
	for k, v := range headers {
		req.Header.Set(k, v)
	}
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		t.Fatalf("POST %s: %v", url, err)
	}
	return resp
}

// decodeJSON decodes the response body into dst and closes it.
func decodeJSON(t *testing.T, resp *http.Response, dst interface{}) {
	t.Helper()
	defer resp.Body.Close()
	if err := json.NewDecoder(resp.Body).Decode(dst); err != nil {
		t.Fatalf("decode response body: %v", err)
	}
}

// ---- Metrics (:8081) ----

func TestMetrics_PostEvents_Returns201(t *testing.T) {
	ts := metricsServer(t)
	resp := postJSON(t, ts.URL+"/events", map[string]interface{}{
		"type":    "click-mouse",
		"userId":  "u1",
		"payload": map[string]string{"k": "v"},
	}, nil)
	if resp.StatusCode != http.StatusCreated {
		resp.Body.Close()
		t.Fatalf("want 201, got %d", resp.StatusCode)
	}
	var got map[string]interface{}
	decodeJSON(t, resp, &got)
	if got["id"] == nil || got["id"] == "" {
		t.Error("want non-empty id in response")
	}
	if got["type"] != "click-mouse" {
		t.Errorf("want type=click-mouse, got %v", got["type"])
	}
	if got["userId"] != "u1" {
		t.Errorf("want userId=u1, got %v", got["userId"])
	}
}

func TestMetrics_GetEvents_Returns200Array(t *testing.T) {
	ts := metricsServer(t)
	postJSON(t, ts.URL+"/events", map[string]interface{}{
		"type":   "submit-form",
		"userId": "u2",
	}, nil).Body.Close()

	resp, err := http.Get(ts.URL + "/events")
	if err != nil {
		t.Fatalf("GET /events: %v", err)
	}
	if resp.StatusCode != http.StatusOK {
		resp.Body.Close()
		t.Fatalf("want 200, got %d", resp.StatusCode)
	}
	var events []map[string]interface{}
	decodeJSON(t, resp, &events)
	if len(events) != 1 {
		t.Fatalf("want 1 event, got %d", len(events))
	}
	if events[0]["type"] != "submit-form" {
		t.Errorf("want type=submit-form, got %v", events[0]["type"])
	}
}

// ---- IAM (:8082) — lifecycle ----

func TestIAM_PostUsers_Returns201(t *testing.T) {
	ts := iamServer(t)
	resp := postJSON(t, ts.URL+"/users", map[string]string{
		"username": "alice",
		"password": "s3cret",
	}, nil)
	if resp.StatusCode != http.StatusCreated {
		resp.Body.Close()
		t.Fatalf("want 201, got %d", resp.StatusCode)
	}
	var got map[string]string
	decodeJSON(t, resp, &got)
	if got["id"] == "" {
		t.Error("want non-empty id")
	}
	if got["username"] != "alice" {
		t.Errorf("want username=alice, got %v", got["username"])
	}
}

func TestIAM_GetUser_Returns200(t *testing.T) {
	ts := iamServer(t)
	cr := postJSON(t, ts.URL+"/users", map[string]string{
		"username": "bob",
		"password": "pw",
	}, nil)
	var created map[string]string
	decodeJSON(t, cr, &created)

	resp, err := http.Get(fmt.Sprintf("%s/users/%s", ts.URL, created["id"]))
	if err != nil {
		t.Fatalf("GET /users/{id}: %v", err)
	}
	if resp.StatusCode != http.StatusOK {
		resp.Body.Close()
		t.Fatalf("want 200, got %d", resp.StatusCode)
	}
	var got map[string]string
	decodeJSON(t, resp, &got)
	if got["id"] != created["id"] || got["username"] != "bob" {
		t.Errorf("unexpected user body: %v", got)
	}
}

func TestIAM_DeleteUser_Returns200(t *testing.T) {
	ts := iamServer(t)
	cr := postJSON(t, ts.URL+"/users", map[string]string{
		"username": "carol",
		"password": "pw",
	}, nil)
	var created map[string]string
	decodeJSON(t, cr, &created)

	req, _ := http.NewRequest(http.MethodDelete, fmt.Sprintf("%s/users/%s", ts.URL, created["id"]), nil)
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		t.Fatalf("DELETE /users/{id}: %v", err)
	}
	resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		t.Fatalf("want 200, got %d", resp.StatusCode)
	}
}

func TestIAM_AuthLogin_Returns200WithToken(t *testing.T) {
	ts := iamServer(t)
	postJSON(t, ts.URL+"/users", map[string]string{
		"username": "dave",
		"password": "pw",
	}, nil).Body.Close()

	resp := postJSON(t, ts.URL+"/auth/login", map[string]string{
		"username": "dave",
		"password": "pw",
	}, nil)
	if resp.StatusCode != http.StatusOK {
		resp.Body.Close()
		t.Fatalf("want 200, got %d", resp.StatusCode)
	}
	var got map[string]string
	decodeJSON(t, resp, &got)
	if got["token"] == "" {
		t.Error("want non-empty token in login response")
	}
}

func TestIAM_AuthLogout_Returns200(t *testing.T) {
	ts := iamServer(t)
	postJSON(t, ts.URL+"/users", map[string]string{
		"username": "eve",
		"password": "pw",
	}, nil).Body.Close()

	loginResp := postJSON(t, ts.URL+"/auth/login", map[string]string{
		"username": "eve",
		"password": "pw",
	}, nil)
	var loginBody map[string]string
	decodeJSON(t, loginResp, &loginBody)

	resp := postJSON(t, ts.URL+"/auth/logout", nil, map[string]string{
		"Authorization": "Bearer " + loginBody["token"],
	})
	resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		t.Fatalf("want 200, got %d", resp.StatusCode)
	}
}

// ---- IAM (:8082) — authz ----

func TestIAM_PostRoles_Returns201(t *testing.T) {
	ts := iamServer(t)
	resp := postJSON(t, ts.URL+"/roles", map[string]interface{}{
		"name":        "admin",
		"permissions": []string{"read", "write"},
	}, nil)
	if resp.StatusCode != http.StatusCreated {
		resp.Body.Close()
		t.Fatalf("want 201, got %d", resp.StatusCode)
	}
	var got map[string]interface{}
	decodeJSON(t, resp, &got)
	if got["id"] == nil || got["id"] == "" {
		t.Error("want non-empty id")
	}
	if got["name"] != "admin" {
		t.Errorf("want name=admin, got %v", got["name"])
	}
}

func TestIAM_GetRoles_Returns200Array(t *testing.T) {
	ts := iamServer(t)
	postJSON(t, ts.URL+"/roles", map[string]interface{}{
		"name":        "viewer",
		"permissions": []string{"read"},
	}, nil).Body.Close()

	resp, err := http.Get(ts.URL + "/roles")
	if err != nil {
		t.Fatalf("GET /roles: %v", err)
	}
	if resp.StatusCode != http.StatusOK {
		resp.Body.Close()
		t.Fatalf("want 200, got %d", resp.StatusCode)
	}
	var roles []map[string]interface{}
	decodeJSON(t, resp, &roles)
	if len(roles) != 1 {
		t.Fatalf("want 1 role, got %d", len(roles))
	}
	if roles[0]["name"] != "viewer" {
		t.Errorf("want name=viewer, got %v", roles[0]["name"])
	}
}

func TestIAM_PostUserRoles_Returns201(t *testing.T) {
	ts := iamServer(t)

	ur := postJSON(t, ts.URL+"/users", map[string]string{
		"username": "frank",
		"password": "pw",
	}, nil)
	var user map[string]string
	decodeJSON(t, ur, &user)

	rr := postJSON(t, ts.URL+"/roles", map[string]interface{}{
		"name":        "member",
		"permissions": []string{"read"},
	}, nil)
	var role map[string]interface{}
	decodeJSON(t, rr, &role)

	resp := postJSON(t, fmt.Sprintf("%s/users/%s/roles", ts.URL, user["id"]), map[string]string{
		"roleId": role["id"].(string),
	}, nil)
	resp.Body.Close()
	if resp.StatusCode != http.StatusCreated {
		t.Fatalf("want 201, got %d", resp.StatusCode)
	}
}

func TestIAM_GetUserRoles_Returns200Array(t *testing.T) {
	ts := iamServer(t)

	ur := postJSON(t, ts.URL+"/users", map[string]string{
		"username": "grace",
		"password": "pw",
	}, nil)
	var user map[string]string
	decodeJSON(t, ur, &user)

	rr := postJSON(t, ts.URL+"/roles", map[string]interface{}{
		"name":        "editor",
		"permissions": []string{"write"},
	}, nil)
	var role map[string]interface{}
	decodeJSON(t, rr, &role)

	postJSON(t, fmt.Sprintf("%s/users/%s/roles", ts.URL, user["id"]), map[string]string{
		"roleId": role["id"].(string),
	}, nil).Body.Close()

	resp, err := http.Get(fmt.Sprintf("%s/users/%s/roles", ts.URL, user["id"]))
	if err != nil {
		t.Fatalf("GET /users/{id}/roles: %v", err)
	}
	if resp.StatusCode != http.StatusOK {
		resp.Body.Close()
		t.Fatalf("want 200, got %d", resp.StatusCode)
	}
	var roles []map[string]interface{}
	decodeJSON(t, resp, &roles)
	if len(roles) != 1 {
		t.Fatalf("want 1 role, got %d", len(roles))
	}
}

func TestIAM_AuthzCheck_Returns200WithAllowed(t *testing.T) {
	ts := iamServer(t)

	ur := postJSON(t, ts.URL+"/users", map[string]string{
		"username": "henry",
		"password": "pw",
	}, nil)
	var user map[string]string
	decodeJSON(t, ur, &user)

	rr := postJSON(t, ts.URL+"/roles", map[string]interface{}{
		"name":        "superuser",
		"permissions": []string{"delete"},
	}, nil)
	var role map[string]interface{}
	decodeJSON(t, rr, &role)

	postJSON(t, fmt.Sprintf("%s/users/%s/roles", ts.URL, user["id"]), map[string]string{
		"roleId": role["id"].(string),
	}, nil).Body.Close()

	// Permission the user has → allowed=true
	resp := postJSON(t, ts.URL+"/authz/check", map[string]string{
		"userId":     user["id"],
		"permission": "delete",
	}, nil)
	if resp.StatusCode != http.StatusOK {
		resp.Body.Close()
		t.Fatalf("want 200, got %d", resp.StatusCode)
	}
	var got map[string]bool
	decodeJSON(t, resp, &got)
	if !got["allowed"] {
		t.Error("want allowed=true for granted permission")
	}

	// Permission the user does not have → allowed=false
	resp2 := postJSON(t, ts.URL+"/authz/check", map[string]string{
		"userId":     user["id"],
		"permission": "nonexistent",
	}, nil)
	if resp2.StatusCode != http.StatusOK {
		resp2.Body.Close()
		t.Fatalf("want 200 for denied check, got %d", resp2.StatusCode)
	}
	var got2 map[string]bool
	decodeJSON(t, resp2, &got2)
	if got2["allowed"] {
		t.Error("want allowed=false for ungranted permission")
	}
}
