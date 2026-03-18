// Package smoke validates the gold test framework helpers without running
// the pipeline. Uses a committed minimal stub binary as the fixture.
//
// Run with: go test ./... (no build tag required)
package smoke_test

import (
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"testing"
	"time"

	"github.com/cornjacket/ai-builder/tests/regression/goldutil"
)

const stubPort = "9099"
const stubAddr = "http://localhost:" + stubPort

// fixtureDir returns the absolute path to the fixture package.
func fixtureDir(t *testing.T) string {
	t.Helper()
	wd, err := os.Getwd()
	if err != nil {
		t.Fatalf("os.Getwd: %v", err)
	}
	// smoke/ is at tests/regression/infra-smoke/smoke/
	// fixture is at  tests/regression/infra-smoke/fixture/cmd/stub/
	return filepath.Clean(filepath.Join(wd, "../fixture/cmd/stub"))
}

// fixtureRoot returns the path to the fixture tree root (contains cmd/stub/main.go).
func fixtureRoot(t *testing.T) string {
	t.Helper()
	wd, err := os.Getwd()
	if err != nil {
		t.Fatalf("os.Getwd: %v", err)
	}
	return filepath.Clean(filepath.Join(wd, "../fixture"))
}

// TestFindMainPackage verifies that FindMainPackage locates the fixture binary.
func TestFindMainPackage(t *testing.T) {
	root := fixtureRoot(t)
	pkg, err := goldutil.FindMainPackage(root)
	if err != nil {
		t.Fatalf("FindMainPackage: unexpected error: %v", err)
	}
	if pkg == "" {
		t.Fatalf("FindMainPackage(%s): returned empty string, expected cmd/stub directory", root)
	}
	want := fixtureDir(t)
	if filepath.Clean(pkg) != filepath.Clean(want) {
		t.Fatalf("FindMainPackage: got %q, want %q", pkg, want)
	}
}

// TestFindMainPackages verifies that FindMainPackages returns exactly one package.
func TestFindMainPackages(t *testing.T) {
	root := fixtureRoot(t)
	pkgs, err := goldutil.FindMainPackages(root)
	if err != nil {
		t.Fatalf("FindMainPackages: unexpected error: %v", err)
	}
	if len(pkgs) != 1 {
		t.Fatalf("FindMainPackages(%s): got %d packages, want 1: %v", root, len(pkgs), pkgs)
	}
	want := fixtureDir(t)
	if filepath.Clean(pkgs[0]) != filepath.Clean(want) {
		t.Fatalf("FindMainPackages: got %q, want %q", pkgs[0], want)
	}
}

// TestBuildBinary verifies that BuildBinary compiles the fixture successfully.
func TestBuildBinary(t *testing.T) {
	bin := filepath.Join(t.TempDir(), "stub")
	if err := goldutil.BuildBinary(fixtureDir(t), bin); err != nil {
		t.Fatalf("BuildBinary: %v", err)
	}
	if _, err := os.Stat(bin); err != nil {
		t.Fatalf("BuildBinary: binary not found at %s: %v", bin, err)
	}
}

// TestWaitReady verifies that WaitReady detects a live listener and times out
// correctly when no listener is present.
func TestWaitReady(t *testing.T) {
	bin := filepath.Join(t.TempDir(), "stub")
	if err := goldutil.BuildBinary(fixtureDir(t), bin); err != nil {
		t.Fatalf("BuildBinary: %v", err)
	}

	t.Run("TimesOutWhenNoListener", func(t *testing.T) {
		err := goldutil.WaitReady("http://localhost:19099/", 300*time.Millisecond)
		if err == nil {
			t.Fatal("WaitReady: expected timeout error, got nil")
		}
	})

	t.Run("DetectsLiveListener", func(t *testing.T) {
		cmd := exec.Command(bin)
		cmd.Env = append(os.Environ(), fmt.Sprintf("PORT=%s", stubPort))
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		if err := cmd.Start(); err != nil {
			t.Fatalf("start stub: %v", err)
		}
		defer func() {
			cmd.Process.Kill()
			cmd.Wait()
		}()

		if err := goldutil.WaitReady(stubAddr+"/", 5*time.Second); err != nil {
			t.Fatalf("WaitReady: %v", err)
		}
	})
}

// TestMustDo verifies that MustDo sends a request and returns a response.
func TestMustDo(t *testing.T) {
	bin := filepath.Join(t.TempDir(), "stub")
	if err := goldutil.BuildBinary(fixtureDir(t), bin); err != nil {
		t.Fatalf("BuildBinary: %v", err)
	}

	cmd := exec.Command(bin)
	cmd.Env = append(os.Environ(), fmt.Sprintf("PORT=%s", stubPort))
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if err := cmd.Start(); err != nil {
		t.Fatalf("start stub: %v", err)
	}
	defer func() {
		cmd.Process.Kill()
		cmd.Wait()
	}()

	if err := goldutil.WaitReady(stubAddr+"/", 5*time.Second); err != nil {
		t.Fatalf("WaitReady: %v", err)
	}

	resp := goldutil.MustDo(t, "GET", stubAddr+"/", "")
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		t.Fatalf("MustDo GET /: want 200, got %d", resp.StatusCode)
	}
}

// TestExtractField verifies field extraction from JSON objects.
func TestExtractField(t *testing.T) {
	m := map[string]interface{}{
		"id":   "abc123",
		"name": "Alice",
	}

	if got := goldutil.ExtractField(m, "id"); got != "abc123" {
		t.Errorf("ExtractField(id): want abc123, got %q", got)
	}
	if got := goldutil.ExtractField(m, "missing", "id"); got != "abc123" {
		t.Errorf("ExtractField(missing,id): want abc123, got %q", got)
	}
	if got := goldutil.ExtractField(m, "nothere"); got != "" {
		t.Errorf("ExtractField(nothere): want empty, got %q", got)
	}
}
