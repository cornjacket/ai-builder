//go:build regression

package ai_builder_test

import (
	"reflect"
	"testing"

	"github.com/cornjacket/ai-builder/tests/regression/fibonacci/work/fibonacci"
)

func TestCompute(t *testing.T) {
	tests := []struct {
		name  string
		input int
		want  []int
	}{
		{"n=-1", -1, []int{}},
		{"n=0", 0, []int{}},
		{"n=1", 1, []int{0}},
		{"n=2", 2, []int{0, 1}},
		{"n=5", 5, []int{0, 1, 1, 2, 3}},
		{"n=10", 10, []int{0, 1, 1, 2, 3, 5, 8, 13, 21, 34}},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := fibonacci.Compute(tt.input)
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("Compute(%d) = %v; want %v", tt.input, got, tt.want)
			}
		})
	}
}
