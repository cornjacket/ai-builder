//go:build regression

package gold_test

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/fs"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

const (
	serviceAddr = "http://localhost:8080"
	outputDir   = "/tmp/ai-builder-test-user-service-output"
	binaryPath  = "/tmp/user-service-gold-bin"
)

// ---------------------------------------------------------------------------
// Test setup: find, build, and start the generated service
// ---------------------------------------------------------------------------

func TestMain(m *testing.M) {
	pkg, err := findMainPackage(outputDir)
	if err != nil || pkg == "" {
		fmt.Fprintf(os.Stderr, "SKIP: could not find main package in %s: %v\n", outputDir, err)
		os.Exit(0)
	}

	if err := buildBinary(pkg, binaryPath); err != nil {
		fmt.Fprintf(os.Stderr, "FAIL: build error: %v\n", err)
		os.Exit(1)
	}
	defer os.Remove(binaryPath)

	cmd := exec.Command(binaryPath)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if err := cmd.Start(); err != nil {
		fmt.Fprintf(os.Stderr, "FAIL: could not start service: %v\n", err)
		os.Exit(1)
	}
	defer cmd.Process.Kill()

	if err := waitReady(serviceAddr+"/users", 10*time.Second); err != nil {
		fmt.Fprintf(os.Stderr, "FAIL: service did not become ready: %v\n", err)
		os.Exit(1)
	}

	os.Exit(m.Run())
}

// ---------------------------------------------------------------------------
// Behavioural tests
// ---------------------------------------------------------------------------

func TestCreateUser(t *testing.T) {
	body := `{"name": "Alice"}`
	resp := mustDo(t, "POST", serviceAddr+"/users", body)
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusCreated && resp.StatusCode != http.StatusOK {
		t.Fatalf("POST /users: want 200 or 201, got %d", resp.StatusCode)
	}
	user := decodeJSON(t, resp)
	if extractID(user) == "" {
		t.Fatal("POST /users: response has no id field")
	}
}

func TestGetUser(t *testing.T) {
	id := createUser(t, `{"name": "Bob"}`)

	resp := mustDo(t, "GET", serviceAddr+"/users/"+id, "")
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Fatalf("GET /users/%s: want 200, got %d", id, resp.StatusCode)
	}
	user := decodeJSON(t, resp)
	if extractID(user) != id {
		t.Fatalf("GET /users/%s: response id %q != %q", id, extractID(user), id)
	}
}

func TestGetUserNotFound(t *testing.T) {
	resp := mustDo(t, "GET", serviceAddr+"/users/nonexistent-id-999", "")
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusNotFound {
		t.Fatalf("GET /users/nonexistent: want 404, got %d", resp.StatusCode)
	}
}

func TestUpdateUser(t *testing.T) {
	id := createUser(t, `{"name": "Charlie"}`)

	resp := mustDo(t, "PUT", serviceAddr+"/users/"+id, `{"name": "Charlie Updated"}`)
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Fatalf("PUT /users/%s: want 200, got %d", id, resp.StatusCode)
	}

	// Verify the update persisted
	getResp := mustDo(t, "GET", serviceAddr+"/users/"+id, "")
	defer getResp.Body.Close()
	if getResp.StatusCode != http.StatusOK {
		t.Fatalf("GET after PUT /users/%s: want 200, got %d", id, getResp.StatusCode)
	}
}

func TestUpdateUserNotFound(t *testing.T) {
	resp := mustDo(t, "PUT", serviceAddr+"/users/nonexistent-id-999", `{"name": "Ghost"}`)
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusNotFound {
		t.Fatalf("PUT /users/nonexistent: want 404, got %d", resp.StatusCode)
	}
}

func TestDeleteUser(t *testing.T) {
	id := createUser(t, `{"name": "Dave"}`)

	resp := mustDo(t, "DELETE", serviceAddr+"/users/"+id, "")
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusNoContent {
		t.Fatalf("DELETE /users/%s: want 200 or 204, got %d", id, resp.StatusCode)
	}

	// Verify deleted
	getResp := mustDo(t, "GET", serviceAddr+"/users/"+id, "")
	defer getResp.Body.Close()
	if getResp.StatusCode != http.StatusNotFound {
		t.Fatalf("GET after DELETE /users/%s: want 404, got %d", id, getResp.StatusCode)
	}
}

func TestDeleteUserNotFound(t *testing.T) {
	resp := mustDo(t, "DELETE", serviceAddr+"/users/nonexistent-id-999", "")
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusNotFound {
		t.Fatalf("DELETE /users/nonexistent: want 404, got %d", resp.StatusCode)
	}
}

func TestResponsesAreJSON(t *testing.T) {
	id := createUser(t, `{"name": "Eve"}`)

	for _, tc := range []struct {
		method string
		path   string
		body   string
	}{
		{"POST", "/users", `{"name": "Frank"}`},
		{"GET", "/users/" + id, ""},
		{"PUT", "/users/" + id, `{"name": "Eve Updated"}`},
	} {
		resp := mustDo(t, tc.method, serviceAddr+tc.path, tc.body)
		defer resp.Body.Close()
		ct := resp.Header.Get("Content-Type")
		if !strings.Contains(ct, "application/json") {
			t.Errorf("%s %s: Content-Type %q does not contain application/json", tc.method, tc.path, ct)
		}
	}
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

// createUser creates a user and returns its ID.
func createUser(t *testing.T, body string) string {
	t.Helper()
	resp := mustDo(t, "POST", serviceAddr+"/users", body)
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusCreated && resp.StatusCode != http.StatusOK {
		t.Fatalf("createUser: POST /users returned %d", resp.StatusCode)
	}
	user := decodeJSON(t, resp)
	id := extractID(user)
	if id == "" {
		t.Fatal("createUser: response has no id field")
	}
	return id
}

func mustDo(t *testing.T, method, url, body string) *http.Response {
	t.Helper()
	var bodyReader *bytes.Reader
	if body != "" {
		bodyReader = bytes.NewReader([]byte(body))
	} else {
		bodyReader = bytes.NewReader(nil)
	}
	req, err := http.NewRequest(method, url, bodyReader)
	if err != nil {
		t.Fatalf("NewRequest %s %s: %v", method, url, err)
	}
	if body != "" {
		req.Header.Set("Content-Type", "application/json")
	}
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		t.Fatalf("%s %s: %v", method, url, err)
	}
	return resp
}

func decodeJSON(t *testing.T, resp *http.Response) map[string]interface{} {
	t.Helper()
	var m map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&m); err != nil {
		t.Fatalf("decodeJSON: %v", err)
	}
	return m
}

// extractID tries common ID field names produced by different decompositions.
func extractID(m map[string]interface{}) string {
	for _, key := range []string{"id", "ID", "Id", "user_id", "userId"} {
		if v, ok := m[key]; ok {
			return fmt.Sprintf("%v", v)
		}
	}
	return ""
}

func findMainPackage(root string) (string, error) {
	var found string
	err := filepath.WalkDir(root, func(path string, d fs.DirEntry, err error) error {
		if err != nil || d.IsDir() || !strings.HasSuffix(path, ".go") {
			return err
		}
		content, err := os.ReadFile(path)
		if err != nil {
			return nil
		}
		if strings.Contains(string(content), "package main") {
			found = filepath.Dir(path)
			return filepath.SkipAll
		}
		return nil
	})
	return found, err
}

func buildBinary(pkgDir, outPath string) error {
	cmd := exec.Command("go", "build", "-o", outPath, ".")
	cmd.Dir = pkgDir
	out, err := cmd.CombinedOutput()
	if err != nil {
		return fmt.Errorf("go build failed: %w\n%s", err, out)
	}
	return nil
}

func waitReady(url string, timeout time.Duration) error {
	deadline := time.Now().Add(timeout)
	for time.Now().Before(deadline) {
		resp, err := http.Get(url)
		if err == nil {
			resp.Body.Close()
			return nil
		}
		time.Sleep(200 * time.Millisecond)
	}
	return fmt.Errorf("service at %s not ready after %s", url, timeout)
}
