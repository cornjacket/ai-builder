"""
Build a master documentation index from an output directory tree.

Walks the output directory, extracts Purpose: and Tags: from every .md file
(excluding README.md and master-index.md), and produces a single index file
with header depth mirroring directory depth.

Any content between <!-- user-doc-start --> and <!-- user-doc-end --> in an
existing master-index.md is preserved across rebuilds.

Usage (CLI):
    python3 build_master_index.py --output-dir path/to/output [--dest master-index.md]

Usage (in-process):
    from build_master_index import build_master_index
    build_master_index(output_dir, dest)
"""

import argparse
import re
from pathlib import Path


_USER_START = "<!-- user-doc-start -->"
_USER_END   = "<!-- user-doc-end -->"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_master_index(output_dir: Path, dest: Path | None = None) -> None:
    """Walk output_dir, build the index, and write it to dest.

    dest defaults to output_dir / "master-index.md".
    Preserves any user sentinel blocks from a previous run.
    """
    if dest is None:
        dest = output_dir / "master-index.md"

    user_blocks = _extract_user_blocks(dest)
    entries = _collect_entries(output_dir)
    content = _render_index(output_dir, entries, user_blocks)
    dest.write_text(content)


# ---------------------------------------------------------------------------
# Collection
# ---------------------------------------------------------------------------

def _collect_entries(output_dir: Path) -> list[dict]:
    """Return a list of entry dicts for every qualifying .md file.

    Excluded:
    - master-index.md (the file we're writing)
    - README.md at the output_dir root (the build-level README rendered by render_readme.py)
    - README.md files in subdirectories ARE included — ARCHITECT writes component-level
      README.md files with Purpose:/Tags: headers and those are the primary indexed docs.
    """
    entries = []
    for md_path in sorted(output_dir.rglob("*.md")):
        if md_path.name == "master-index.md":
            continue
        if md_path.name == "README.md" and md_path.parent == output_dir:
            continue  # skip root-level build README only
        purpose, tags = _extract_header(md_path)
        if not purpose and not tags:
            continue  # skip files with no Purpose/Tags header
        rel = md_path.relative_to(output_dir)
        depth = len(rel.parts) - 1  # depth of the directory containing the file
        entries.append({
            "path":    rel,
            "dir":     rel.parent,
            "depth":   depth,
            "purpose": purpose,
            "tags":    tags,
        })
    return entries


def _extract_header(md_path: Path) -> tuple[str, str]:
    """Return (purpose_first_sentence, tags) from the doc-format.md header block.

    The header block looks like:
        Purpose: Some description here.
        Tags: tag1, tag2
    """
    purpose = ""
    tags    = ""
    try:
        for line in md_path.read_text(errors="replace").splitlines()[:10]:
            line = line.strip()
            if line.startswith("Purpose:"):
                text = line[len("Purpose:"):].strip()
                # Take first sentence only
                m = re.match(r'^([^.!?]+[.!?])', text)
                purpose = m.group(1).strip() if m else text
            elif line.startswith("Tags:"):
                tags = line[len("Tags:"):].strip()
    except Exception:
        pass
    return purpose, tags


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def _render_index(output_dir: Path, entries: list[dict], user_blocks: dict[str, str]) -> str:
    title = output_dir.name
    lines = [f"# {title}", ""]

    # Group entries by directory
    by_dir: dict[Path, list[dict]] = {}
    for e in entries:
        by_dir.setdefault(e["dir"], []).append(e)

    # Emit each directory section in sorted order
    for dir_path in sorted(by_dir.keys()):
        dir_entries = by_dir[dir_path]
        depth = dir_entries[0]["depth"]
        header_level = "#" * min(depth + 2, 6)  # ## for depth-0, ### for depth-1, etc.

        section_title = str(dir_path) if dir_path != Path(".") else title
        lines += [f"{header_level} {section_title}", ""]

        # User block for this directory (if any)
        user_key = str(dir_path)
        if user_key in user_blocks:
            lines += [_USER_START, user_blocks[user_key], _USER_END, ""]

        # Table of files
        lines += [
            "| File | Tags | Description |",
            "|------|------|-------------|",
        ]
        for e in sorted(dir_entries, key=lambda x: x["path"].name):
            fname = e["path"].name
            lines.append(f"| {fname} | {e['tags']} | {e['purpose']} |")
        lines.append("")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# User block preservation
# ---------------------------------------------------------------------------

def _extract_user_blocks(dest: Path) -> dict[str, str]:
    """Return {section_title: block_content} for each user sentinel block in dest."""
    if not dest.exists():
        return {}

    blocks  = {}
    content = dest.read_text()
    current_section = ""

    for line in content.splitlines():
        # Track which section we're in by looking at the most recent heading
        m = re.match(r'^(#{1,6})\s+(.+)$', line)
        if m:
            current_section = m.group(2).strip()

        if _USER_START in line:
            # Collect until end marker
            start = content.index(_USER_START, content.index(line))
            end   = content.find(_USER_END, start)
            if end != -1:
                inner = content[start + len(_USER_START):end].strip()
                if inner:
                    blocks[current_section] = inner
    return blocks


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _main() -> None:
    parser = argparse.ArgumentParser(description="Build master documentation index")
    parser.add_argument("--output-dir", required=True, type=Path, help="Root of the output directory")
    parser.add_argument("--dest",       type=Path, default=None,  help="Destination file (default: output-dir/master-index.md)")
    args = parser.parse_args()

    if not args.output_dir.exists():
        print(f"Error: {args.output_dir} does not exist")
        raise SystemExit(1)

    dest = args.dest or args.output_dir / "master-index.md"
    build_master_index(args.output_dir, dest)
    print(f"Wrote {dest}")


if __name__ == "__main__":
    _main()
