# Subtask: add-reviews-directory-to-target

| Field    | Value                |
|----------|----------------------|
| Status   | —                    |
| Epic     | main             |
| Tags     | oracle, tooling             |
| Parent   | 37a660-design-oracle-and-pipeline-phases           |
| Priority | MED         |

## Description

Add `project/reviews/` to the `target/` skeleton and update the installation
scripts to create it in new target repos.

**Blocked by:** `9b9d18-design-reviews-directory` — directory structure and
review artifact format must be decided before this subtask can be implemented.

**Changes:**

- Add `target/project/reviews/` with a `.gitkeep` placeholder and a
  `review-template.md` (format defined by the design subtask)
- Update `target/setup-project.sh` to create `project/reviews/` when
  installing into a target repo
- Update `target/verify-setup.sh` to check that `project/reviews/` exists
- Update `target/SETUP.md` to document `project/reviews/`
- Mirror the `project/reviews/` directory in the ai-builder scratchpad
  (`/Users/david/Go/src/github.com/cornjacket/ai-builder-target/`) during
  end-to-end testing

## Notes

Depends on `9b9d18-design-reviews-directory`.
