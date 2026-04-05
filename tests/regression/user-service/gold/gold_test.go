//go:build regression

package gold_test

import (
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/cornjacket/ai-builder/tests/regression/goldutil"
)

const (
	serviceAddr = "http://localhost:8080"
)

var (
	outputDir  string
	targetDir  string
	binaryPath string
)

func init() {
	wd, err := os.Getwd()
	if err != nil {
		panic(err)
	}
	root := filepath.Clean(filepath.Join(wd, "../../../../"))
	outputDir = filepath.Join(root, "sandbox/regressions/user-service/output")
	targetDir = filepath.Join(root, "sandbox/regressions/user-service/target")
	binaryPath = filepath.Join(root, "sandbox/user-service-bin")
}

// ---------------------------------------------------------------------------
// Test setup: find, build, and start the generated service
// ---------------------------------------------------------------------------

func TestMain(m *testing.M) {
	pkg, err := goldutil.FindMainPackage(outputDir)
	if err != nil || pkg == "" {
		fmt.Fprintf(os.Stderr, "SKIP: could not find main package in %s: %v\n", outputDir, err)
		os.Exit(0)
	}

	if err := goldutil.BuildBinary(pkg, binaryPath); err != nil {
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

	if err := goldutil.WaitReady(serviceAddr+"/users", 10*time.Second); err != nil {
		fmt.Fprintf(os.Stderr, "FAIL: service did not become ready: %v\n", err)
		os.Exit(1)
	}

	os.Exit(m.Run())
}

// ---------------------------------------------------------------------------
// Documentation coverage
// ---------------------------------------------------------------------------

func TestReadmeCoverage(t *testing.T) {
	goldutil.CheckReadmeCoverage(t, outputDir)
}

func TestSubtasksComplete(t *testing.T) {
	goldutil.CheckSubtasksComplete(t, targetDir)
}

func TestRunSummaryExists(t *testing.T) {
	goldutil.CheckRunSummaryExists(t, targetDir)
}

func TestRetryWarnings(t *testing.T) {
	goldutil.CheckRetryWarnings(t, targetDir, 0)
}

// ---------------------------------------------------------------------------
// Behavioural tests
// ---------------------------------------------------------------------------

func TestCreateUser(t *testing.T) {
	resp := goldutil.MustDo(t, "POST", serviceAddr+"/users", `{"name": "Alice"}`)
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusCreated && resp.StatusCode != http.StatusOK {
		t.Fatalf("POST /users: want 200 or 201, got %d", resp.StatusCode)
	}
	user := goldutil.DecodeJSON(t, resp)
	if goldutil.ExtractField(user, "id", "ID", "Id", "user_id", "userId") == "" {
		t.Fatal("POST /users: response has no id field")
	}
}

func TestGetUser(t *testing.T) {
	id := createUser(t, `{"name": "Bob"}`)

	resp := goldutil.MustDo(t, "GET", serviceAddr+"/users/"+id, "")
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Fatalf("GET /users/%s: want 200, got %d", id, resp.StatusCode)
	}
	user := goldutil.DecodeJSON(t, resp)
	if goldutil.ExtractField(user, "id", "ID", "Id", "user_id", "userId") != id {
		t.Fatalf("GET /users/%s: response id %q != %q", id, goldutil.ExtractField(user, "id", "ID", "Id", "user_id", "userId"), id)
	}
}

func TestGetUserNotFound(t *testing.T) {
	resp := goldutil.MustDo(t, "GET", serviceAddr+"/users/nonexistent-id-999", "")
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusNotFound {
		t.Fatalf("GET /users/nonexistent: want 404, got %d", resp.StatusCode)
	}
}

func TestUpdateUser(t *testing.T) {
	id := createUser(t, `{"name": "Charlie"}`)

	resp := goldutil.MustDo(t, "PUT", serviceAddr+"/users/"+id, `{"name": "Charlie Updated"}`)
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Fatalf("PUT /users/%s: want 200, got %d", id, resp.StatusCode)
	}

	getResp := goldutil.MustDo(t, "GET", serviceAddr+"/users/"+id, "")
	defer getResp.Body.Close()
	if getResp.StatusCode != http.StatusOK {
		t.Fatalf("GET after PUT /users/%s: want 200, got %d", id, getResp.StatusCode)
	}
}

func TestUpdateUserNotFound(t *testing.T) {
	resp := goldutil.MustDo(t, "PUT", serviceAddr+"/users/nonexistent-id-999", `{"name": "Ghost"}`)
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusNotFound {
		t.Fatalf("PUT /users/nonexistent: want 404, got %d", resp.StatusCode)
	}
}

func TestDeleteUser(t *testing.T) {
	id := createUser(t, `{"name": "Dave"}`)

	resp := goldutil.MustDo(t, "DELETE", serviceAddr+"/users/"+id, "")
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusNoContent {
		t.Fatalf("DELETE /users/%s: want 200 or 204, got %d", id, resp.StatusCode)
	}

	getResp := goldutil.MustDo(t, "GET", serviceAddr+"/users/"+id, "")
	defer getResp.Body.Close()
	if getResp.StatusCode != http.StatusNotFound {
		t.Fatalf("GET after DELETE /users/%s: want 404, got %d", id, getResp.StatusCode)
	}
}

func TestDeleteUserNotFound(t *testing.T) {
	resp := goldutil.MustDo(t, "DELETE", serviceAddr+"/users/nonexistent-id-999", "")
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
		resp := goldutil.MustDo(t, tc.method, serviceAddr+tc.path, tc.body)
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

func createUser(t *testing.T, body string) string {
	t.Helper()
	resp := goldutil.MustDo(t, "POST", serviceAddr+"/users", body)
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusCreated && resp.StatusCode != http.StatusOK {
		t.Fatalf("createUser: POST /users returned %d", resp.StatusCode)
	}
	user := goldutil.DecodeJSON(t, resp)
	id := goldutil.ExtractField(user, "id", "ID", "Id", "user_id", "userId")
	if id == "" {
		t.Fatal("createUser: response has no id field")
	}
	return id
}
