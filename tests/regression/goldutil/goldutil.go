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


// CheckReadmeCoverage validates README.md presence and absence at directory
// levels within outputDir according to architectural relevance rules for Go
// projects:
//
//   - A directory named exactly "internal" is a Go language visibility boundary.
//     It must NOT have a README.md. Its absence is asserted.
//   - Any other directory that directly contains .go files (a Go package) MUST
//     have a README.md.
//   - Any other directory whose immediate children include Go packages (a
//     composite source level) MUST have a README.md.
//   - The output root directory itself is not checked.
//
// All failures are accumulated and reported via t.Errorf — the function never
// calls t.Fatalf, so every violation is reported in a single test run.
func CheckReadmeCoverage(t *testing.T, outputDir string) {
	t.Helper()

	err := filepath.WalkDir(outputDir, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if !d.IsDir() {
			return nil
		}
		if path == outputDir {
			return nil // skip the output root
		}

		rel, _ := filepath.Rel(outputDir, path)
		base := filepath.Base(path)
		readmePath := filepath.Join(path, "README.md")
		hasReadme := fileExists(readmePath)

		if base == "internal" {
			// Go language convention — not a design boundary; README must not exist.
			if hasReadme {
				t.Errorf("README.md must not exist in language-convention directory: %s/", rel)
			}
			return nil
		}

		// Architecturally relevant: contains Go source files directly (a package),
		// or directly contains child directories that contain Go source files (a composite).
		if isGoPackageDir(path) || hasGoPackageChildren(path) {
			if !hasReadme {
				t.Errorf("missing README.md in architecturally relevant directory: %s/", rel)
			}
		}

		return nil
	})
	if err != nil {
		t.Errorf("CheckReadmeCoverage: directory walk error: %v", err)
	}
}

// fileExists reports whether the named file exists and is not a directory.
func fileExists(path string) bool {
	info, err := os.Stat(path)
	return err == nil && !info.IsDir()
}

// isGoPackageDir reports whether dir directly contains at least one .go file.
func isGoPackageDir(dir string) bool {
	entries, err := os.ReadDir(dir)
	if err != nil {
		return false
	}
	for _, e := range entries {
		if !e.IsDir() && strings.HasSuffix(e.Name(), ".go") {
			return true
		}
	}
	return false
}

// hasGoPackageChildren reports whether dir has at least one immediate
// subdirectory that directly contains .go files.
func hasGoPackageChildren(dir string) bool {
	entries, err := os.ReadDir(dir)
	if err != nil {
		return false
	}
	for _, e := range entries {
		if e.IsDir() && isGoPackageDir(filepath.Join(dir, e.Name())) {
			return true
		}
	}
	return false
}

// CheckRunSummaryExists walks all completed TOP-level pipeline task directories
// (X-prefixed directories that contain a task.json with "level": "TOP") and
// asserts that the sibling README.md contains a "## Run Summary" section. Its
// absence means the final write_metrics_to_task_json(final=True) call failed —
// typically caused by the build directory being renamed before the orchestrator
// could flush its final metrics.
func CheckRunSummaryExists(t *testing.T, targetDir string) {
	t.Helper()

	err := filepath.WalkDir(targetDir, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if !d.IsDir() || !strings.HasPrefix(filepath.Base(path), "X-") {
			return nil
		}
		tjPath := filepath.Join(path, "task.json")
		if !fileExists(tjPath) {
			return nil
		}
		raw, err := os.ReadFile(tjPath)
		if err != nil {
			return nil
		}
		var tj map[string]interface{}
		if err := json.Unmarshal(raw, &tj); err != nil {
			return nil
		}
		if tj["level"] != "TOP" {
			return nil
		}
		// Only the pipeline entry point (build-N) should have a Run Summary.
		// Component tasks may also carry level=TOP but their parent directory
		// is a pipeline task (has a task.json). Skip those.
		parentTaskJSON := filepath.Join(filepath.Dir(path), "task.json")
		if fileExists(parentTaskJSON) {
			return nil
		}
		readmePath := filepath.Join(path, "README.md")
		content, err := os.ReadFile(readmePath)
		if err != nil {
			rel, _ := filepath.Rel(targetDir, readmePath)
			t.Errorf("TOP pipeline task missing README.md: %s", rel)
			return nil
		}
		if !strings.Contains(string(content), "## Run Summary") {
			rel, _ := filepath.Rel(targetDir, readmePath)
			t.Errorf("TOP pipeline task README missing Run Summary section: %s", rel)
		}
		return nil
	})
	if err != nil {
		t.Errorf("CheckRunSummaryExists: walk error: %v", err)
	}
}

// CheckSubtasksComplete walks all README.md files inside X-prefixed pipeline
// task directories under targetDir and reports an error for any incomplete
// subtask (a line matching "- [ ]"). An X-prefixed directory is one whose
// base name starts with "X-"; these represent tasks that the pipeline has
// marked complete. Any incomplete subtask entry left behind indicates that
// the completion handler failed to update the README before the directory
// was renamed.
func CheckSubtasksComplete(t *testing.T, targetDir string) {
	t.Helper()

	err := filepath.WalkDir(targetDir, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if d.IsDir() || d.Name() != "README.md" {
			return nil
		}
		dir := filepath.Dir(path)
		if !strings.HasPrefix(filepath.Base(dir), "X-") {
			return nil
		}
		// Only check pipeline task READMEs (directory has a sibling task.json)
		if !fileExists(filepath.Join(dir, "task.json")) {
			return nil
		}
		content, err := os.ReadFile(path)
		if err != nil {
			return nil
		}
		rel, _ := filepath.Rel(targetDir, path)
		for i, line := range strings.Split(string(content), "\n") {
			if strings.Contains(line, "- [ ]") {
				t.Errorf("incomplete subtask in completed pipeline task %s line %d: %s",
					rel, i+1, strings.TrimSpace(line))
			}
		}
		return nil
	})
	if err != nil {
		t.Errorf("CheckSubtasksComplete: walk error: %v", err)
	}
}

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
