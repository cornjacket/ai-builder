# roles/

AI agent prompt files for the builder machine. These are injected as the
role prompt for ARCHITECT and IMPLEMENTOR when the builder machine is active.

| File | Role | Description |
|------|------|-------------|
| `ARCHITECT.md` | ARCHITECT | Designs components; operates in decompose or design mode |
| `IMPLEMENTOR.md` | IMPLEMENTOR | Implements code from ARCHITECT's design |

These files must be self-contained — agents run with `cwd=/tmp` and cannot
follow external file references at runtime. All format rules (Purpose/Tags
headers, version number policy) are inlined directly.
