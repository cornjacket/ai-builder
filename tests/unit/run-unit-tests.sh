#!/usr/bin/env bash
# Run the full unit test suite for ai-builder.
#
# Usage:
#   run-unit-tests.sh [--python] [--shell] [--coverage]
#
# With no flags, runs both Python and shell suites.
# --python   run Python tests only (via pytest)
# --shell    run shell tests only  (via bats)
# --coverage add pytest-cov report (Python suite only)
#
# Exit code: 0 if all enabled suites pass, 1 if any fail.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# ---------------------------------------------------------------------------
# Flags
# ---------------------------------------------------------------------------

RUN_PYTHON=false
RUN_SHELL=false
COVERAGE=false

# Default: run everything when no suite flags given
_no_suite_flags=true

while [[ $# -gt 0 ]]; do
    case "$1" in
        --python)   RUN_PYTHON=true; _no_suite_flags=false; shift ;;
        --shell)    RUN_SHELL=true;  _no_suite_flags=false; shift ;;
        --coverage) COVERAGE=true;   shift ;;
        *) echo "Unknown flag: $1"; exit 1 ;;
    esac
done

if [[ "$_no_suite_flags" == true ]]; then
    RUN_PYTHON=true
    RUN_SHELL=true
fi

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_pass=0
_fail=0

_header() { echo ""; echo "==> $1"; echo ""; }

# ---------------------------------------------------------------------------
# Python suite
# ---------------------------------------------------------------------------

run_python() {
    _header "Python unit tests (pytest)"

    local pytest_args=("$REPO_ROOT/tests/unit" "-v" "--tb=short")

    if [[ "$COVERAGE" == true ]]; then
        pytest_args+=(
            "--cov=$REPO_ROOT/ai-builder/orchestrator"
            "--cov-report=term-missing"
        )
    fi

    if pytest "${pytest_args[@]}"; then
        echo ""
        echo "  [PASS] Python suite"
        (( _pass++ )) || true
    else
        echo ""
        echo "  [FAIL] Python suite"
        (( _fail++ )) || true
    fi
}

# ---------------------------------------------------------------------------
# Shell suite (bats)
# ---------------------------------------------------------------------------

run_shell() {
    _header "Shell unit tests (bats)"

    local shell_dir="$REPO_ROOT/tests/unit/shell"

    if ! command -v bats &>/dev/null; then
        echo "  [SKIP] bats not found — install bats-core to run shell tests"
        return
    fi

    if [[ ! -d "$shell_dir" ]] || [[ -z "$(ls "$shell_dir"/*.bats 2>/dev/null)" ]]; then
        echo "  [SKIP] no .bats files found in tests/unit/shell/"
        return
    fi

    if bats "$shell_dir"; then
        echo ""
        echo "  [PASS] Shell suite"
        (( _pass++ )) || true
    else
        echo ""
        echo "  [FAIL] Shell suite"
        (( _fail++ )) || true
    fi
}

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

echo "ai-builder unit test runner"
echo "repo: $REPO_ROOT"

[[ "$RUN_PYTHON" == true ]] && run_python
[[ "$RUN_SHELL"  == true ]] && run_shell

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

echo ""
echo "---"
echo "Results: ${_pass} passed, ${_fail} failed"

if [[ $_fail -gt 0 ]]; then
    exit 1
fi
