#!/usr/bin/env bash
# Write the absolute path of a task README to current-job.txt in the pipeline
# output directory.
#
# Used by Oracle before invoking the orchestrator, by TM after selecting the
# next task, and by regression test reset scripts during setup.
#
# Usage:
#   set-current-job.sh --output-dir <pipeline-output-dir> <task-readme-path>
#
# Example:
#   set-current-job.sh \
#       --output-dir tests/regression/fibonacci/work \
#       project/tasks/main/in-progress/abc123-my-task/README.md

set -euo pipefail

OUTPUT_DIR=""
README_PATH=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
        -*) echo "Unknown flag: $1"; exit 1 ;;
        *) README_PATH="$1"; shift ;;
    esac
done

if [[ -z "$OUTPUT_DIR" || -z "$README_PATH" ]]; then
    echo "Usage: set-current-job.sh --output-dir <pipeline-output-dir> <task-readme-path>"
    exit 1
fi

if [[ ! -f "$README_PATH" ]]; then
    echo "Task README not found: $README_PATH"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"
echo "$(cd "$(dirname "$README_PATH")" && pwd)/$(basename "$README_PATH")" > "$OUTPUT_DIR/current-job.txt"
echo "current-job.txt -> $(cat "$OUTPUT_DIR/current-job.txt")"
