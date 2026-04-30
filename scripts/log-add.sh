#!/usr/bin/env bash
# Append an entry to log.md, or back-fill the most recent _pending_ hash.
#
# Append mode (writes log.md with _pending_ as the hash placeholder):
#   scripts/log-add.sh --task <task-name> [--subtask <subtask-name>] [--epic <epic>] -- <description>
#
# Back-fill mode (replaces the most recent _pending_ with `git rev-parse --short HEAD`):
#   scripts/log-add.sh --backfill
#
# In both modes the script writes to log.md only — it does NOT commit. Stage
# log.md alongside the work it describes and commit normally. After the commit
# lands, run --backfill; the resulting dirty log.md rides into the next task's
# commit (per lesson 038, never make a dedicated back-fill commit).
#
# Task and subtask names must match an existing directory under
# project/tasks/<epic>/{draft,backlog,in-progress,complete,wont-do}/. Completed
# tasks/subtasks may be on disk with an `X-` prefix; the script tolerates both.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="$REPO_ROOT/log.md"

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------

MODE=""
TASK=""
SUBTASK=""
EPIC="main"
DESCRIPTION=""

usage() {
    cat <<EOF >&2
Usage:
  $0 --task <task-name> [--subtask <subtask-name>] [--epic <epic>] -- <description>
  $0 --backfill
EOF
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --task)     TASK="$2";    shift 2 ;;
        --subtask)  SUBTASK="$2"; shift 2 ;;
        --epic)     EPIC="$2";    shift 2 ;;
        --backfill) MODE="backfill"; shift ;;
        --)         shift; DESCRIPTION="$*"; break ;;
        -h|--help)  usage ;;
        *)          echo "Unknown flag: $1" >&2; usage ;;
    esac
done

if [[ "$MODE" != "backfill" ]]; then
    if [[ -n "$TASK" || -n "$DESCRIPTION" ]]; then
        MODE="append"
    else
        usage
    fi
fi

if [[ ! -f "$LOG_FILE" ]]; then
    echo "ERROR: $LOG_FILE not found." >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Back-fill mode
# ---------------------------------------------------------------------------

if [[ "$MODE" == "backfill" ]]; then
    if ! grep -q '`_pending_`' "$LOG_FILE"; then
        echo "ERROR: no \`_pending_\` entries found in $LOG_FILE." >&2
        exit 1
    fi

    HASH=$(git -C "$REPO_ROOT" rev-parse --short HEAD)

    # Replace only the LAST occurrence of `_pending_`.
    awk -v hash="$HASH" '
        { lines[NR] = $0 }
        /`_pending_`/ { last = NR }
        END {
            for (i = 1; i <= NR; i++) {
                if (i == last) {
                    sub(/`_pending_`/, "`" hash "`", lines[i])
                }
                print lines[i]
            }
        }
    ' "$LOG_FILE" > "$LOG_FILE.tmp"
    mv "$LOG_FILE.tmp" "$LOG_FILE"

    echo "Back-filled hash: $HASH"
    echo "log.md is now dirty — let it ride into the next task's commit."
    exit 0
fi

# ---------------------------------------------------------------------------
# Append mode
# ---------------------------------------------------------------------------

if [[ -z "$TASK" || -z "$DESCRIPTION" ]]; then
    usage
fi

# Resolve the task: search the four status folders for a matching directory.
TASK_DIR=""
for folder in draft backlog in-progress complete wont-do; do
    candidate="$REPO_ROOT/project/tasks/$EPIC/$folder/$TASK"
    if [[ -d "$candidate" ]]; then
        TASK_DIR="$candidate"
        break
    fi
done

if [[ -z "$TASK_DIR" ]]; then
    echo "ERROR: task '$TASK' not found under project/tasks/$EPIC/{draft,backlog,in-progress,complete,wont-do}/" >&2
    exit 1
fi

# Resolve subtask (if given): match either <name> or X-<name> under TASK_DIR.
if [[ -n "$SUBTASK" ]]; then
    if [[ ! -d "$TASK_DIR/$SUBTASK" && ! -d "$TASK_DIR/X-$SUBTASK" ]]; then
        echo "ERROR: subtask '$SUBTASK' not found under $TASK_DIR/" >&2
        exit 1
    fi
fi

DATE=$(date +%Y-%m-%d)

if [[ -n "$SUBTASK" ]]; then
    ENTRY="- **$DATE** — $DESCRIPTION Task: \`$TASK\`. Subtask: \`$SUBTASK\`. Commit: \`_pending_\`."
else
    ENTRY="- **$DATE** — $DESCRIPTION Task: \`$TASK\`. Commit: \`_pending_\`."
fi

# Description should already end with a period; add one if missing so the
# rendered sentence is clean.
case "$DESCRIPTION" in
    *.|*!|*\?) ;;
    *)
        if [[ -n "$SUBTASK" ]]; then
            ENTRY="- **$DATE** — $DESCRIPTION. Task: \`$TASK\`. Subtask: \`$SUBTASK\`. Commit: \`_pending_\`."
        else
            ENTRY="- **$DATE** — $DESCRIPTION. Task: \`$TASK\`. Commit: \`_pending_\`."
        fi
        ;;
esac

# Append entry to log.md (always at end of file).
printf '%s\n' "$ENTRY" >> "$LOG_FILE"

echo "Appended entry to log.md:"
echo "  $ENTRY"
echo ""
echo "Stage log.md alongside your other changes and commit normally."
echo "After committing, run: $0 --backfill"
