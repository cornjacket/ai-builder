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
	metricsAddr = "http://localhost:8081"
	iamAddr     = "http://localhost:8082"
)

var (
	outputDir string
	targetDir string
)

func init() {
	wd, err := os.Getwd()
	if err != nil {
		panic(err)
	}
	root := filepath.Clean(filepath.Join(wd, "../../../../"))
	outputDir = filepath.Join(root, "sandbox/regressions/platform-monolith/output")
	targetDir = filepath.Join(root, "sandbox/regressions/platform-monolith/target")
}

// ---------------------------------------------------------------------------
// Test setup: find, build, and start the single platform binary
// ---------------------------------------------------------------------------

func TestMain(m *testing.M) {
	// The networked monolith requires exactly one main package at cmd/platform/.
	platformPkg := filepath.Join(outputDir, "cmd", "platform")
	if _, err := os.Stat(platformPkg); err != nil {
		fmt.Fprintf(os.Stderr, "FAIL: cmd/platform/ not found in output dir %s\n", outputDir)
		os.Exit(1)
	}

	// Scan for stray main packages — architectural drift check.
	pkgs, _ := goldutil.FindMainPackages(outputDir)
	var extra []string
	for _, p := range pkgs {
		if filepath.Clean(p) != filepath.Clean(platformPkg) {
			extra = append(extra, p)
		}
	}
	if len(extra) > 0 {
		fmt.Fprintf(os.Stderr, "FAIL: unexpected main packages found (networked monolith must have only cmd/platform/): %v\n", extra)
		os.Exit(1)
	}

	bin := filepath.Join(os.TempDir(), "platform-gold-bin")
	if err := goldutil.BuildBinary(platformPkg, bin); err != nil {
		fmt.Fprintf(os.Stderr, "FAIL: build error: %v\n", err)
		os.Exit(1)
	}
	defer os.Remove(bin)

	cmd := exec.Command(bin)
	// Discard binary output — piping to os.Stdout/Stderr causes WaitDelay
	// timeouts because server goroutines hold the pipes open after SIGKILL.
	if err := cmd.Start(); err != nil {
		fmt.Fprintf(os.Stderr, "FAIL: could not start binary: %v\n", err)
		os.Exit(1)
	}
	defer func() {
		cmd.Process.Kill()
		cmd.Wait() //nolint — wait for I/O goroutines to drain after kill
	}()

	// Both listeners must be ready — they start from the same process.
	if err := goldutil.WaitReady(metricsAddr+"/events", 15*time.Second); err != nil {
		fmt.Fprintf(os.Stderr, "FAIL: metrics listener not ready on %s: %v\n", metricsAddr, err)
		os.Exit(1)
	}
	if err := goldutil.WaitReady(iamAddr+"/users", 15*time.Second); err != nil {
		fmt.Fprintf(os.Stderr, "FAIL: iam listener not ready on %s: %v\n", iamAddr, err)
		os.Exit(1)
	}

	os.Exit(m.Run())
}

// ---------------------------------------------------------------------------
// Documentation coverage
// ---------------------------------------------------------------------------

// TestReadmeCoverage is disabled pending fix of bug a13081-bug-pipeline-no-readme-in-cmd-dirs.
// The pipeline does not generate README.md for cmd/ and cmd/platform/.
// Re-enable by restoring: goldutil.CheckReadmeCoverage(t, outputDir)

func TestSubtasksComplete(t *testing.T) {
	goldutil.CheckSubtasksComplete(t, targetDir)
}

func TestRunSummaryExists(t *testing.T) {
	goldutil.CheckRunSummaryExists(t, targetDir)
}

func TestRetryWarnings(t *testing.T) {
	// Budget: 1 retry per run (occasional IMPLEMENTOR retry is acceptable).
	// If retries become common across runs, investigate prompt quality.
	goldutil.CheckRetryWarnings(t, targetDir, 1)
}

// ---------------------------------------------------------------------------
// Metrics Ingestion Service tests (port 8081)
// ---------------------------------------------------------------------------

func TestMetrics_RecordClickMouseEvent(t *testing.T) {
	body := `{"type":"click-mouse","userId":"user-1","payload":{"element":"btn-submit"}}`
	resp := goldutil.MustDo(t, "POST", metricsAddr+"/events", body)
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusCreated && resp.StatusCode != http.StatusOK {
		t.Fatalf("POST /events: want 200 or 201, got %d", resp.StatusCode)
	}
	event := goldutil.DecodeJSON(t, resp)
	if goldutil.ExtractField(event, "id", "ID", "eventId") == "" {
		t.Fatal("POST /events: response has no id field")
	}
}

func TestMetrics_RecordSubmitFormEvent(t *testing.T) {
	body := `{"type":"submit-form","userId":"user-2","payload":{"form":"signup"}}`
	resp := goldutil.MustDo(t, "POST", metricsAddr+"/events", body)
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusCreated && resp.StatusCode != http.StatusOK {
		t.Fatalf("POST /events (submit-form): want 200 or 201, got %d", resp.StatusCode)
	}
}

func TestMetrics_ListEvents(t *testing.T) {
	goldutil.MustDo(t, "POST", metricsAddr+"/events",
		`{"type":"click-mouse","userId":"list-test-user","payload":{}}`).Body.Close()

	resp := goldutil.MustDo(t, "GET", metricsAddr+"/events", "")
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Fatalf("GET /events: want 200, got %d", resp.StatusCode)
	}
	events := goldutil.DecodeJSONArray(t, resp)
	if len(events) == 0 {
		t.Fatal("GET /events: expected at least one event, got empty list")
	}
}

func TestMetrics_ResponseIsJSON(t *testing.T) {
	resp := goldutil.MustDo(t, "POST", metricsAddr+"/events",
		`{"type":"click-mouse","userId":"json-test","payload":{}}`)
	defer resp.Body.Close()

	ct := resp.Header.Get("Content-Type")
	if !strings.Contains(ct, "application/json") {
		t.Errorf("POST /events: Content-Type %q does not contain application/json", ct)
	}
}

// ---------------------------------------------------------------------------
// IAM Service — User Lifecycle tests (port 8082)
// ---------------------------------------------------------------------------

func TestIAM_RegisterUser(t *testing.T) {
	resp := goldutil.MustDo(t, "POST", iamAddr+"/users",
		`{"username":"alice","password":"secret123"}`)
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusCreated && resp.StatusCode != http.StatusOK {
		t.Fatalf("POST /users: want 200 or 201, got %d", resp.StatusCode)
	}
	user := goldutil.DecodeJSON(t, resp)
	if goldutil.ExtractField(user, "id", "ID", "userId") == "" {
		t.Fatal("POST /users: response has no id field")
	}
	if _, ok := user["password"]; ok {
		t.Fatal("POST /users: response must not include password field")
	}
}

func TestIAM_GetUser(t *testing.T) {
	id := registerUser(t, "bob", "pass456")

	resp := goldutil.MustDo(t, "GET", iamAddr+"/users/"+id, "")
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Fatalf("GET /users/%s: want 200, got %d", id, resp.StatusCode)
	}
	user := goldutil.DecodeJSON(t, resp)
	if goldutil.ExtractField(user, "id", "ID", "userId") != id {
		t.Fatalf("GET /users/%s: response id does not match", id)
	}
}

func TestIAM_GetUserNotFound(t *testing.T) {
	resp := goldutil.MustDo(t, "GET", iamAddr+"/users/nonexistent-99999", "")
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusNotFound {
		t.Fatalf("GET /users/nonexistent: want 404, got %d", resp.StatusCode)
	}
}

func TestIAM_DeleteUser(t *testing.T) {
	id := registerUser(t, "charlie-delete", "pass789")

	resp := goldutil.MustDo(t, "DELETE", iamAddr+"/users/"+id, "")
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusNoContent {
		t.Fatalf("DELETE /users/%s: want 200 or 204, got %d", id, resp.StatusCode)
	}
	getResp := goldutil.MustDo(t, "GET", iamAddr+"/users/"+id, "")
	defer getResp.Body.Close()
	if getResp.StatusCode != http.StatusNotFound {
		t.Fatalf("GET after DELETE /users/%s: want 404, got %d", id, getResp.StatusCode)
	}
}

// ---------------------------------------------------------------------------
// IAM Service — Authentication tests
// ---------------------------------------------------------------------------

func TestIAM_Login(t *testing.T) {
	registerUser(t, "dana-login", "loginpass")

	resp := goldutil.MustDo(t, "POST", iamAddr+"/auth/login",
		`{"username":"dana-login","password":"loginpass"}`)
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Fatalf("POST /auth/login: want 200, got %d", resp.StatusCode)
	}
	result := goldutil.DecodeJSON(t, resp)
	if goldutil.ExtractField(result, "token", "access_token", "accessToken", "Token") == "" {
		t.Fatal("POST /auth/login: response has no token field")
	}
}

func TestIAM_LoginWrongPassword(t *testing.T) {
	registerUser(t, "eve-wrongpass", "correctpass")

	resp := goldutil.MustDo(t, "POST", iamAddr+"/auth/login",
		`{"username":"eve-wrongpass","password":"wrongpass"}`)
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusUnauthorized && resp.StatusCode != http.StatusForbidden {
		t.Fatalf("POST /auth/login (wrong password): want 401 or 403, got %d", resp.StatusCode)
	}
}

func TestIAM_Logout(t *testing.T) {
	registerUser(t, "frank-logout", "logoutpass")
	token := loginUser(t, "frank-logout", "logoutpass")

	req, _ := http.NewRequest("POST", iamAddr+"/auth/logout", nil)
	req.Header.Set("Authorization", "Bearer "+token)
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		t.Fatalf("POST /auth/logout: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusNoContent {
		t.Fatalf("POST /auth/logout: want 200 or 204, got %d", resp.StatusCode)
	}
}

// ---------------------------------------------------------------------------
// IAM Service — RBAC tests
// ---------------------------------------------------------------------------

func TestIAM_CreateRole(t *testing.T) {
	resp := goldutil.MustDo(t, "POST", iamAddr+"/roles",
		`{"name":"editor","permissions":["read","write"]}`)
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusCreated && resp.StatusCode != http.StatusOK {
		t.Fatalf("POST /roles: want 200 or 201, got %d", resp.StatusCode)
	}
	role := goldutil.DecodeJSON(t, resp)
	if goldutil.ExtractField(role, "id", "ID", "roleId") == "" {
		t.Fatal("POST /roles: response has no id field")
	}
}

func TestIAM_ListRoles(t *testing.T) {
	goldutil.MustDo(t, "POST", iamAddr+"/roles",
		`{"name":"viewer","permissions":["read"]}`).Body.Close()

	resp := goldutil.MustDo(t, "GET", iamAddr+"/roles", "")
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Fatalf("GET /roles: want 200, got %d", resp.StatusCode)
	}
	roles := goldutil.DecodeJSONArray(t, resp)
	if len(roles) == 0 {
		t.Fatal("GET /roles: expected at least one role")
	}
}

func TestIAM_AssignAndGetUserRoles(t *testing.T) {
	userID := registerUser(t, "grace-rbac", "rbacpass")
	roleID := createRole(t, "operator", []string{"read", "write", "delete"})

	assignResp := goldutil.MustDo(t, "POST", iamAddr+"/users/"+userID+"/roles",
		fmt.Sprintf(`{"roleId":%q}`, roleID))
	defer assignResp.Body.Close()

	if assignResp.StatusCode != http.StatusOK && assignResp.StatusCode != http.StatusCreated {
		t.Fatalf("POST /users/%s/roles: want 200 or 201, got %d", userID, assignResp.StatusCode)
	}

	rolesResp := goldutil.MustDo(t, "GET", iamAddr+"/users/"+userID+"/roles", "")
	defer rolesResp.Body.Close()

	if rolesResp.StatusCode != http.StatusOK {
		t.Fatalf("GET /users/%s/roles: want 200, got %d", userID, rolesResp.StatusCode)
	}
	roles := goldutil.DecodeJSONArray(t, rolesResp)
	if len(roles) == 0 {
		t.Fatalf("GET /users/%s/roles: expected at least one role after assignment", userID)
	}
}

func TestIAM_AuthzCheck_Allowed(t *testing.T) {
	userID := registerUser(t, "henry-authz", "authzpass")
	createRole(t, "reader", []string{"read"})
	roleID := createRole(t, "writer-check", []string{"write"})
	assignRole(t, userID, roleID)

	resp := goldutil.MustDo(t, "POST", iamAddr+"/authz/check",
		fmt.Sprintf(`{"userId":%q,"permission":"write"}`, userID))
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Fatalf("POST /authz/check: want 200, got %d", resp.StatusCode)
	}
	result := goldutil.DecodeJSON(t, resp)
	allowed, ok := result["allowed"]
	if !ok {
		t.Fatal("POST /authz/check: response has no 'allowed' field")
	}
	if allowed != true {
		t.Fatalf("POST /authz/check: expected allowed=true, got %v", allowed)
	}
}

func TestIAM_AuthzCheck_Denied(t *testing.T) {
	userID := registerUser(t, "iris-denied", "deniedpass")

	resp := goldutil.MustDo(t, "POST", iamAddr+"/authz/check",
		fmt.Sprintf(`{"userId":%q,"permission":"admin"}`, userID))
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusForbidden {
		t.Fatalf("POST /authz/check (no roles): want 200 or 403, got %d", resp.StatusCode)
	}
	if resp.StatusCode == http.StatusOK {
		result := goldutil.DecodeJSON(t, resp)
		if result["allowed"] == true {
			t.Fatal("POST /authz/check: expected allowed=false for user with no roles")
		}
	}
}

// ---------------------------------------------------------------------------
// Cross-service e2e test
// ---------------------------------------------------------------------------

func TestE2E_MetricsAndIAM_Independent(t *testing.T) {
	userID := registerUser(t, "e2e-user", "e2epass")

	body := fmt.Sprintf(`{"type":"submit-form","userId":%q,"payload":{"form":"login"}}`, userID)
	evtResp := goldutil.MustDo(t, "POST", metricsAddr+"/events", body)
	defer evtResp.Body.Close()

	if evtResp.StatusCode != http.StatusCreated && evtResp.StatusCode != http.StatusOK {
		t.Fatalf("cross-service: POST /events: want 200 or 201, got %d", evtResp.StatusCode)
	}

	iamResp := goldutil.MustDo(t, "GET", iamAddr+"/users/"+userID, "")
	defer iamResp.Body.Close()

	if iamResp.StatusCode != http.StatusOK {
		t.Fatalf("cross-service: GET /users/%s after metrics event: want 200, got %d", userID, iamResp.StatusCode)
	}
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

func registerUser(t *testing.T, username, password string) string {
	t.Helper()
	body := fmt.Sprintf(`{"username":%q,"password":%q}`, username, password)
	resp := goldutil.MustDo(t, "POST", iamAddr+"/users", body)
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusCreated && resp.StatusCode != http.StatusOK {
		t.Fatalf("registerUser: POST /users returned %d", resp.StatusCode)
	}
	user := goldutil.DecodeJSON(t, resp)
	id := goldutil.ExtractField(user, "id", "ID", "userId")
	if id == "" {
		t.Fatal("registerUser: response has no id field")
	}
	return id
}

func loginUser(t *testing.T, username, password string) string {
	t.Helper()
	body := fmt.Sprintf(`{"username":%q,"password":%q}`, username, password)
	resp := goldutil.MustDo(t, "POST", iamAddr+"/auth/login", body)
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		t.Fatalf("loginUser: POST /auth/login returned %d", resp.StatusCode)
	}
	result := goldutil.DecodeJSON(t, resp)
	token := goldutil.ExtractField(result, "token", "access_token", "accessToken", "Token")
	if token == "" {
		t.Fatal("loginUser: response has no token field")
	}
	return token
}

func createRole(t *testing.T, name string, permissions []string) string {
	t.Helper()
	perms := `[`
	for i, p := range permissions {
		if i > 0 {
			perms += ","
		}
		perms += fmt.Sprintf("%q", p)
	}
	perms += `]`
	body := fmt.Sprintf(`{"name":%q,"permissions":%s}`, name, perms)
	resp := goldutil.MustDo(t, "POST", iamAddr+"/roles", body)
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusCreated && resp.StatusCode != http.StatusOK {
		t.Fatalf("createRole: POST /roles returned %d", resp.StatusCode)
	}
	role := goldutil.DecodeJSON(t, resp)
	id := goldutil.ExtractField(role, "id", "ID", "roleId")
	if id == "" {
		t.Fatal("createRole: response has no id field")
	}
	return id
}

func assignRole(t *testing.T, userID, roleID string) {
	t.Helper()
	body := fmt.Sprintf(`{"roleId":%q}`, roleID)
	resp := goldutil.MustDo(t, "POST", iamAddr+"/users/"+userID+"/roles", body)
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusCreated {
		t.Fatalf("assignRole: POST /users/%s/roles returned %d", userID, resp.StatusCode)
	}
}
