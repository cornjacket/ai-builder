//go:build regression

package gold_test

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/cornjacket/ai-builder/tests/regression/goldutil"
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
	outputDir = filepath.Join(root, "sandbox/regressions/doc-user-service/output")
	targetDir = filepath.Join(root, "sandbox/regressions/doc-user-service/target")
}

// checkFile asserts that a file exists at the given path relative to outputDir.
func checkFile(t *testing.T, rel string) {
	t.Helper()
	path := filepath.Join(outputDir, rel)
	if _, err := os.Stat(path); os.IsNotExist(err) {
		t.Errorf("expected file missing: %s", rel)
	}
}

// checkNoSourceModified asserts that no .go files were modified by the pipeline.
// We verify by checking that .go files still exist (not deleted).
func checkSourceIntact(t *testing.T, rel string) {
	t.Helper()
	path := filepath.Join(outputDir, rel)
	if _, err := os.Stat(path); os.IsNotExist(err) {
		t.Errorf("source file missing (pipeline must not delete source): %s", rel)
	}
}

// ---------------------------------------------------------------------------
// README.md files — one per source directory
// ---------------------------------------------------------------------------

func TestRootReadmeExists(t *testing.T) {
	checkFile(t, "README.md")
}

func TestInternalReadmeExists(t *testing.T) {
	checkFile(t, "internal/README.md")
}

func TestUserserviceReadmeExists(t *testing.T) {
	checkFile(t, "internal/userservice/README.md")
}

func TestStoreReadmeExists(t *testing.T) {
	checkFile(t, "internal/userservice/store/README.md")
}

func TestHandlersReadmeExists(t *testing.T) {
	checkFile(t, "internal/userservice/handlers/README.md")
}

// ---------------------------------------------------------------------------
// data-flow.md files — one per composite node (always required)
// ---------------------------------------------------------------------------

func TestRootDataFlowExists(t *testing.T) {
	checkFile(t, "data-flow.md")
}

func TestInternalDataFlowExists(t *testing.T) {
	checkFile(t, "internal/data-flow.md")
}

func TestUserserviceDataFlowExists(t *testing.T) {
	checkFile(t, "internal/userservice/data-flow.md")
}

// ---------------------------------------------------------------------------
// Companion .md files — one per documented source file
// ---------------------------------------------------------------------------

func TestStoreCompanionExists(t *testing.T) {
	// Accept either store.go.md or store.md
	path1 := filepath.Join(outputDir, "internal/userservice/store/store.go.md")
	path2 := filepath.Join(outputDir, "internal/userservice/store/store.md")
	_, err1 := os.Stat(path1)
	_, err2 := os.Stat(path2)
	if os.IsNotExist(err1) && os.IsNotExist(err2) {
		t.Errorf("expected companion doc for store.go (store.go.md or store.md), neither found")
	}
}

func TestHandlersCompanionExists(t *testing.T) {
	path1 := filepath.Join(outputDir, "internal/userservice/handlers/handlers.go.md")
	path2 := filepath.Join(outputDir, "internal/userservice/handlers/handlers.md")
	_, err1 := os.Stat(path1)
	_, err2 := os.Stat(path2)
	if os.IsNotExist(err1) && os.IsNotExist(err2) {
		t.Errorf("expected companion doc for handlers.go (handlers.go.md or handlers.md), neither found")
	}
}

// ---------------------------------------------------------------------------
// Source files must not have been modified or deleted
// ---------------------------------------------------------------------------

func TestSourceFilesIntact(t *testing.T) {
	sources := []string{
		"go.mod",
		"main.go",
		"internal/userservice/store/store.go",
		"internal/userservice/handlers/handlers.go",
	}
	for _, s := range sources {
		checkSourceIntact(t, s)
	}
}

// ---------------------------------------------------------------------------
// Orchestrator teardown outputs
// ---------------------------------------------------------------------------

func TestMasterIndexExists(t *testing.T) {
	checkFile(t, "master-index.md")
}

func TestRetryWarnings(t *testing.T) {
	goldutil.CheckRetryWarnings(t, targetDir, 0)
}

// ---------------------------------------------------------------------------
// No .md files present before run (sanity: template is clean)
// ---------------------------------------------------------------------------

func TestOutputDirExists(t *testing.T) {
	if _, err := os.Stat(outputDir); os.IsNotExist(err) {
		t.Fatalf("output dir does not exist: %s (run reset.sh first)", outputDir)
	}
}
