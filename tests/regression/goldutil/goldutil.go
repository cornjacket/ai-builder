// Package goldutil provides shared test helpers for ai-builder gold (regression) tests.
//
// All functions that accept *testing.T call t.Helper() so failures are
// attributed to the caller's line number, not to this package.
package goldutil

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

// FindMainPackage returns the directory of the first Go file containing
// "package main" found by a depth-first walk of root. Returns ("", nil)
// if no main package exists. Useful for single-binary services.
func FindMainPackage(root string) (string, error) {
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

// FindMainPackages returns the directories of all Go packages containing
// "package main" found under root. Each directory is returned once even if
// it contains multiple .go files. Useful for detecting architectural drift
// (e.g. verifying a monolith has exactly one main package).
func FindMainPackages(root string) ([]string, error) {
	seen := map[string]bool{}
	var pkgs []string
	err := filepath.WalkDir(root, func(path string, d fs.DirEntry, err error) error {
		if err != nil || d.IsDir() || !strings.HasSuffix(path, ".go") {
			return err
		}
		dir := filepath.Dir(path)
		if seen[dir] {
			return nil
		}
		content, err := os.ReadFile(path)
		if err != nil {
			return nil
		}
		if strings.Contains(string(content), "package main") {
			seen[dir] = true
			pkgs = append(pkgs, dir)
		}
		return nil
	})
	return pkgs, err
}

// BuildBinary compiles the Go package at pkgDir and writes the resulting
// binary to outPath. Returns a descriptive error including compiler output
// on failure.
func BuildBinary(pkgDir, outPath string) error {
	cmd := exec.Command("go", "build", "-o", outPath, ".")
	cmd.Dir = pkgDir
	out, err := cmd.CombinedOutput()
	if err != nil {
		return fmt.Errorf("go build failed in %s: %w\n%s", pkgDir, err, out)
	}
	return nil
}

// WaitReady polls url with HTTP GET until it receives any response (any
// status code) or timeout elapses. Returns nil on first successful response.
func WaitReady(url string, timeout time.Duration) error {
	deadline := time.Now().Add(timeout)
	for time.Now().Before(deadline) {
		resp, err := http.Get(url) //nolint:noctx
		if err == nil {
			resp.Body.Close()
			return nil
		}
		time.Sleep(200 * time.Millisecond)
	}
	return fmt.Errorf("service at %s not ready after %s", url, timeout)
}

// MustDo sends an HTTP request and returns the response. Calls t.Fatalf on
// any error. If body is non-empty, sets Content-Type: application/json.
func MustDo(t *testing.T, method, url, body string) *http.Response {
	t.Helper()
	var b *bytes.Reader
	if body != "" {
		b = bytes.NewReader([]byte(body))
	} else {
		b = bytes.NewReader(nil)
	}
	req, err := http.NewRequest(method, url, b)
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

// DecodeJSON decodes the response body as a JSON object. Calls t.Fatalf on
// decode failure.
func DecodeJSON(t *testing.T, resp *http.Response) map[string]interface{} {
	t.Helper()
	var m map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&m); err != nil {
		t.Fatalf("DecodeJSON: %v", err)
	}
	return m
}

// DecodeJSONArray decodes the response body as a JSON array. Calls
// t.Fatalf on decode failure.
func DecodeJSONArray(t *testing.T, resp *http.Response) []interface{} {
	t.Helper()
	var arr []interface{}
	if err := json.NewDecoder(resp.Body).Decode(&arr); err != nil {
		t.Fatalf("DecodeJSONArray: %v", err)
	}
	return arr
}

// ExtractField returns the string value of the first matching key found in m.
// Returns "" if none of the keys are present. Useful for tolerating different
// field naming conventions produced by different model decompositions (e.g.
// "id", "ID", "userId").
func ExtractField(m map[string]interface{}, keys ...string) string {
	for _, key := range keys {
		if v, ok := m[key]; ok {
			return fmt.Sprintf("%v", v)
		}
	}
	return ""
}
