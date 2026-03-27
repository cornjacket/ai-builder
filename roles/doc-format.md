# Documentation Format Convention

All `.md` files written to the output directory by ARCHITECT or IMPLEMENTOR
must include the following header block near the top. For `README.md` files,
a single `# heading` line may appear before the block; the block must then
follow immediately (no other content between the heading and `Purpose:`).
For named docs (e.g. `data-flow.md`), the block must be the very first content.

```
# optional-heading-for-README

Purpose: First sentence — a standalone, complete description of what this file covers.
Additional context sentence(s) if needed. Two to three sentences total maximum.

Tags: <tag1>, <tag2>, ...
```

## Rules

**Purpose field:**
- The first sentence must stand alone as a complete description. DOCUMENTER
  uses it as the index entry — it must be meaningful in isolation.
- Keep it to 2–3 sentences total. If more is needed, the content belongs in
  the body, not the header.
- Write in present tense: "Describes the data flow..." not "This file describes..."

**Tags field:**
- Must appear on the line immediately after the Purpose block (after one blank line).
- Required tags by role:
  - ARCHITECT docs: `Tags: architecture, design`
  - IMPLEMENTOR docs: `Tags: implementation, <component-name>`
- Additional tags are additive. Do not remove the required tags.

## Example — ARCHITECT design doc

```markdown
Purpose: Describes the data flow between the store and handlers components.
Requests enter via handlers, which delegate all persistence to store; no
direct store access from main.go.

Tags: architecture, design

## Data Flow

...
```

## Example — IMPLEMENTOR companion doc

```markdown
Purpose: Documents the non-obvious locking strategy used in the concurrent delete path.
A read lock is insufficient during delete because the existence check and removal
must be atomic.

Tags: implementation, store

## Locking Strategy

...
```
