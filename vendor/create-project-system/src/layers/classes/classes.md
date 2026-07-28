# Worktree Class Definitions

Each task has a `Category:` field assigning it to one of the classes below.
Tasks in the same class touch the same files and should be worked in the same
worktree. Tasks in different classes can run in parallel with minimal merge
conflicts.

**This is a starter file — replace the example class with your own.**

## How it is used

- `new-user-task.sh --category <name>` validates `<name>` against the
  **Worktree branch** values declared here. The literal `unclassified` is
  always accepted, for tasks that fit no class.
- `list-tasks.sh --category <name>` filters by it; `--group-by-category` groups
  output in the order classes are declared in this file.

## Adding a class

Copy the block below. The `**Worktree branch:**` line is the parsed one — its
backticked value is the category name. Everything else is prose for humans.

---

## Class 1 — General

**Worktree branch:** `general`
**Core files:** _list the files this class typically touches_

Starter class so `--category` works out of the box. Replace this with classes
that reflect how your repo actually partitions — group tasks that touch the same
files, so different classes can be worked in parallel worktrees without
conflicting.

**Tasks:** _optional: list task IDs assigned to this class_

---

## Conflict hotspots & merge order

_Once you have several classes, note here which files are touched by more than
one class, and the recommended merge order._
