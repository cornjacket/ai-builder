//go:build regression

package gold_test

import (
	"fmt"
	"io/fs"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
)

var outputDir string

func init() {
	wd, err := os.Getwd()
	if err != nil {
		panic(err)
	}
	root := filepath.Clean(filepath.Join(wd, "../../../../"))
	outputDir = filepath.Join(root, "sandbox/fibonacci-output")
}

// oracleTestSrc is injected into the generated package at test time.
// It calls the generated Compute function with Oracle-specified inputs and
// expected outputs. The spec requires: package fibonacci, func Compute(n int) []int.
const oracleTestSrc = `package fibonacci

import (
	"reflect"
	"testing"
)

func TestGoldCompute(t *testing.T) {
	cases := []struct {
		n    int
		want []int
	}{
		{-1, []int{}},
		{0, []int{}},
		{1, []int{0}},
		{2, []int{0, 1}},
		{5, []int{0, 1, 1, 2, 3}},
		{10, []int{0, 1, 1, 2, 3, 5, 8, 13, 21, 34}},
	}
	for _, tc := range cases {
		got := Compute(tc.n)
		if got == nil {
			got = []int{}
		}
		if !reflect.DeepEqual(got, tc.want) {
			t.Errorf("Compute(%d) = %v; want %v", tc.n, got, tc.want)
		}
	}
}
`

func TestMain(m *testing.M) {
	pkg, err := findGoPackageDir(outputDir)
	if err != nil || pkg == "" {
		fmt.Fprintf(os.Stderr, "SKIP: no Go package found in %s: %v\n", outputDir, err)
		os.Exit(0)
	}
	os.Exit(m.Run())
}

func TestFibonacci_GoldCompute(t *testing.T) {
	pkg, err := findGoPackageDir(outputDir)
	if err != nil || pkg == "" {
		t.Skipf("no Go package found in %s", outputDir)
	}

	tmpFile := filepath.Join(pkg, "zz_gold_oracle_test.go")
	if err := os.WriteFile(tmpFile, []byte(oracleTestSrc), 0644); err != nil {
		t.Fatalf("write oracle test file: %v", err)
	}
	defer os.Remove(tmpFile)

	cmd := exec.Command("go", "test", "-run", "TestGoldCompute", "-v", ".")
	cmd.Dir = pkg
	out, err := cmd.CombinedOutput()
	t.Logf("go test output:\n%s", out)
	if err != nil {
		t.Fatalf("oracle assertions failed: %v", err)
	}
}

// findGoPackageDir returns the directory of the first non-test .go file found
// under root. This locates the generated fibonacci package in the output dir.
func findGoPackageDir(root string) (string, error) {
	var found string
	err := filepath.WalkDir(root, func(path string, d fs.DirEntry, err error) error {
		if err != nil || d.IsDir() || found != "" {
			return err
		}
		if strings.HasSuffix(path, ".go") && !strings.HasSuffix(path, "_test.go") {
			found = filepath.Dir(path)
			return filepath.SkipAll
		}
		return nil
	})
	return found, err
}
