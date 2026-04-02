# linter.py

`MarkdownLinterAgent` — lints `.md` files written in the current pipeline step
and emits typed pass/fail outcomes. Used as `POST_DOC_HANDLER` in the doc
pipeline.

## run(job_doc, output_dir, **kwargs)

**Inputs:**
- `job_doc: Path` — path to the current task README; used to locate `task.json`
- `output_dir: Path` — directory whose `*.md` files are linted

**Reads:**
- `job_doc.parent / task.json` — reads `component_type` field to determine step
  type (`atomic` or `integrate`); defaults to `atomic` if absent or unreadable

**Lints:** all `*.md` files in `output_dir` (non-recursive)

**Checks per file:**
1. `Purpose:` line present
2. `Tags:` line present
3. No empty sections — a heading is considered empty only when the next non-blank
   line is a heading at the SAME or HIGHER level (peer/parent), or when the heading
   is at EOF. A heading followed by a DEEPER sub-heading is NOT flagged as empty,
   because the sub-sections are its content.
4. No placeholder text — rejects `_To be written._`, `TODO`, `FIXME`, `PLACEHOLDER`

**Outcomes:**

| Step type | All pass | Any fail |
|-----------|----------|----------|
| `atomic` | `POST_DOC_HANDLER_ATOMIC_PASS` | `POST_DOC_HANDLER_ATOMIC_FAIL` |
| `integrate` | `POST_DOC_HANDLER_INTEGRATE_PASS` | `POST_DOC_HANDLER_INTEGRATE_FAIL` |

When no `.md` files exist in `output_dir`, emits the pass outcome with a
"nothing to lint" handoff (not an error — some atomic steps produce no docs).

**Returns `AgentResult(exit_code=0, response=...)`** always; failure is
signalled through the outcome token, not the exit code, so the orchestrator
can route back to the writing agent for a retry.

## Module-level helpers

`_check_file(path: Path) -> list[str]` — checks a single file and returns a
list of error strings. Empty list means the file passed all checks. Used
directly in unit tests.

`_find_empty_sections(text: str) -> list[str]` — returns the heading strings
of sections that are empty (no content and no sub-sections). Replaces the
earlier `_EMPTY_SECTION_RE` regex; correctly handles the case where a section's
content consists entirely of sub-headings (those are not empty).

`_PLACEHOLDER_PATTERNS` — list of compiled regexes for the four prohibited
patterns.
