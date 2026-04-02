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
	outputDir = filepath.Join(root, "sandbox/regressions/doc-platform-monolith/output")
	targetDir = filepath.Join(root, "sandbox/regressions/doc-platform-monolith/target")
}

// checkFile asserts that a file exists at the given path relative to outputDir.
func checkFile(t *testing.T, rel string) {
	t.Helper()
	path := filepath.Join(outputDir, rel)
	if _, err := os.Stat(path); os.IsNotExist(err) {
		t.Errorf("expected file missing: %s", rel)
	}
}

// checkSourceIntact asserts that a source file still exists (pipeline must not delete source).
func checkSourceIntact(t *testing.T, rel string) {
	t.Helper()
	path := filepath.Join(outputDir, rel)
	if _, err := os.Stat(path); os.IsNotExist(err) {
		t.Errorf("source file missing (pipeline must not delete source): %s", rel)
	}
}

// ---------------------------------------------------------------------------
// Output dir exists
// ---------------------------------------------------------------------------

func TestOutputDirExists(t *testing.T) {
	if _, err := os.Stat(outputDir); os.IsNotExist(err) {
		t.Fatalf("output dir does not exist: %s (run reset.sh first)", outputDir)
	}
}

// ---------------------------------------------------------------------------
// README.md files — one per directory
// ---------------------------------------------------------------------------

func TestRootReadmeExists(t *testing.T) {
	checkFile(t, "README.md")
}

func TestCmdReadmeExists(t *testing.T) {
	checkFile(t, "cmd/README.md")
}

func TestCmdPlatformReadmeExists(t *testing.T) {
	checkFile(t, "cmd/platform/README.md")
}

func TestInternalReadmeExists(t *testing.T) {
	checkFile(t, "internal/README.md")
}

func TestIamReadmeExists(t *testing.T) {
	// Pre-existing in source template — must still be present after pipeline run
	checkFile(t, "internal/iam/README.md")
}

func TestIamLifecycleReadmeExists(t *testing.T) {
	checkFile(t, "internal/iam/lifecycle/README.md")
}

func TestIamAuthzReadmeExists(t *testing.T) {
	checkFile(t, "internal/iam/authz/README.md")
}

func TestMetricsReadmeExists(t *testing.T) {
	// Pre-existing in source template — must still be present after pipeline run
	checkFile(t, "internal/metrics/README.md")
}

func TestMetricsHandlersReadmeExists(t *testing.T) {
	checkFile(t, "internal/metrics/handlers/README.md")
}

func TestMetricsStoreReadmeExists(t *testing.T) {
	checkFile(t, "internal/metrics/store/README.md")
}

// ---------------------------------------------------------------------------
// Companion .md files — one per documented source file
// ---------------------------------------------------------------------------

func TestMainCompanionExists(t *testing.T) {
	path1 := filepath.Join(outputDir, "cmd/platform/main.go.md")
	path2 := filepath.Join(outputDir, "cmd/platform/main.md")
	_, err1 := os.Stat(path1)
	_, err2 := os.Stat(path2)
	if os.IsNotExist(err1) && os.IsNotExist(err2) {
		t.Errorf("expected companion doc for main.go (main.go.md or main.md), neither found")
	}
}

func TestIamGoCompanionExists(t *testing.T) {
	path1 := filepath.Join(outputDir, "internal/iam/iam.go.md")
	path2 := filepath.Join(outputDir, "internal/iam/iam.md")
	_, err1 := os.Stat(path1)
	_, err2 := os.Stat(path2)
	if os.IsNotExist(err1) && os.IsNotExist(err2) {
		t.Errorf("expected companion doc for iam.go (iam.go.md or iam.md), neither found")
	}
}

func TestLifecycleCompanionExists(t *testing.T) {
	path1 := filepath.Join(outputDir, "internal/iam/lifecycle/lifecycle.go.md")
	path2 := filepath.Join(outputDir, "internal/iam/lifecycle/lifecycle.md")
	_, err1 := os.Stat(path1)
	_, err2 := os.Stat(path2)
	if os.IsNotExist(err1) && os.IsNotExist(err2) {
		t.Errorf("expected companion doc for lifecycle.go (lifecycle.go.md or lifecycle.md), neither found")
	}
}

func TestAuthzCompanionExists(t *testing.T) {
	path1 := filepath.Join(outputDir, "internal/iam/authz/authz.go.md")
	path2 := filepath.Join(outputDir, "internal/iam/authz/authz.md")
	_, err1 := os.Stat(path1)
	_, err2 := os.Stat(path2)
	if os.IsNotExist(err1) && os.IsNotExist(err2) {
		t.Errorf("expected companion doc for authz.go (authz.go.md or authz.md), neither found")
	}
}

func TestMetricsGoCompanionExists(t *testing.T) {
	path1 := filepath.Join(outputDir, "internal/metrics/metrics.go.md")
	path2 := filepath.Join(outputDir, "internal/metrics/metrics.md")
	_, err1 := os.Stat(path1)
	_, err2 := os.Stat(path2)
	if os.IsNotExist(err1) && os.IsNotExist(err2) {
		t.Errorf("expected companion doc for metrics.go (metrics.go.md or metrics.md), neither found")
	}
}

func TestMetricsHandlersCompanionExists(t *testing.T) {
	path1 := filepath.Join(outputDir, "internal/metrics/handlers/handlers.go.md")
	path2 := filepath.Join(outputDir, "internal/metrics/handlers/handlers.md")
	_, err1 := os.Stat(path1)
	_, err2 := os.Stat(path2)
	if os.IsNotExist(err1) && os.IsNotExist(err2) {
		t.Errorf("expected companion doc for handlers.go (handlers.go.md or handlers.md), neither found")
	}
}

func TestMetricsStoreCompanionExists(t *testing.T) {
	path1 := filepath.Join(outputDir, "internal/metrics/store/store.go.md")
	path2 := filepath.Join(outputDir, "internal/metrics/store/store.md")
	_, err1 := os.Stat(path1)
	_, err2 := os.Stat(path2)
	if os.IsNotExist(err1) && os.IsNotExist(err2) {
		t.Errorf("expected companion doc for store.go (store.go.md or store.md), neither found")
	}
}

// ---------------------------------------------------------------------------
// data-flow.md files — one per composite node (always required)
// ---------------------------------------------------------------------------

func TestRootDataFlowExists(t *testing.T) {
	checkFile(t, "data-flow.md")
}

func TestCmdDataFlowExists(t *testing.T) {
	checkFile(t, "cmd/data-flow.md")
}

func TestInternalDataFlowExists(t *testing.T) {
	checkFile(t, "internal/data-flow.md")
}

func TestIamDataFlowExists(t *testing.T) {
	checkFile(t, "internal/iam/data-flow.md")
}

func TestMetricsDataFlowExists(t *testing.T) {
	checkFile(t, "internal/metrics/data-flow.md")
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
// Source files must not have been modified or deleted
// ---------------------------------------------------------------------------

func TestSourceFilesIntact(t *testing.T) {
	sources := []string{
		"go.mod",
		"cmd/platform/main.go",
		"internal/iam/iam.go",
		"internal/iam/lifecycle/lifecycle.go",
		"internal/iam/authz/authz.go",
		"internal/metrics/metrics.go",
		"internal/metrics/handlers/handlers.go",
		"internal/metrics/store/store.go",
	}
	for _, s := range sources {
		checkSourceIntact(t, s)
	}
}
