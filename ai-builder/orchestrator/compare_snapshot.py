#!/usr/bin/env python3
"""
Compare a recording snapshot against the current working tree or another snapshot.

Given a recording dir and an invocation number N, resolves the commit SHA from
recording.json and diffs it against the working tree. An empty diff means the
working tree matches the recording exactly at that invocation point.

Usage:
    compare_snapshot.py --recording <dir> --at N [--against M] [--exclude PATTERN ...]

Examples:
    # Verify the working tree matches the recording after replaying to invocation 5:
    compare_snapshot.py --recording sandbox/regressions/user-service --at 5

    # Same, but exclude volatile log files:
    compare_snapshot.py --recording sandbox/regressions/user-service --at 5 \\
        --exclude output/execution.log --exclude output/logs

    # Inspect what invocation 4 wrote (diff inv-3 vs inv-4):
    compare_snapshot.py --recording sandbox/regressions/user-service --at 3 --against 4

Exit codes:
    0 — no differences (match)
    1 — differences found
    2 — error (missing recording, invalid N, etc.)
"""

import argparse
import sys
from pathlib import Path

# recorder.py lives alongside this script in the orchestrator directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import recorder


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Diff a recording snapshot against the working tree or another snapshot.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--recording",
        type=Path,
        required=True,
        metavar="DIR",
        help="Recording workspace root (must contain recording.json and a .git repo).",
    )
    parser.add_argument(
        "--at",
        type=int,
        required=True,
        metavar="N",
        help="Invocation number to use as the base of the diff.",
    )
    parser.add_argument(
        "--against",
        type=int,
        metavar="M",
        help="If given, diff inv-N against inv-M instead of the working tree.",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        metavar="PATTERN",
        dest="exclude_paths",
        default=[],
        help="Glob pattern to exclude from the diff (repeatable). "
             "E.g. --exclude output/logs --exclude output/execution.log",
    )
    args = parser.parse_args()

    record_dir = args.recording.resolve()
    if not record_dir.exists():
        print(f"error: recording dir not found: {record_dir}", file=sys.stderr)
        sys.exit(2)

    try:
        diff = recorder.diff_snapshot(
            record_dir, args.at,
            against_n=args.against,
            exclude_paths=args.exclude_paths or None,
        )
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(2)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"error: git diff failed: {e}", file=sys.stderr)
        sys.exit(2)

    if diff:
        print(diff, end="")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
