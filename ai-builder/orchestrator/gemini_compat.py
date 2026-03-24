# gemini_compat.py
#
# Gemini CLI compatibility shims for pipeline agent prompts.
#
# Gemini CLI has behavioural differences from Claude Code that require
# role-specific prompt additions to ensure correct operation. This module
# is the single home for all such additions. When a new Gemini-specific
# workaround is needed, add it here rather than scattering fixes across
# orchestrator.py or role prompt files.
#
# Usage:
#   from gemini_compat import gemini_role_addendum
#   if agent == "gemini":
#       prompt += gemini_role_addendum(role)
#
# See sandbox/brainstorm-claude-vs-gemini-behavioral-differences.md for
# the full catalogue of known Claude vs Gemini behavioural differences.


def gemini_role_addendum(role: str) -> str:
    """Return Gemini-specific prompt additions for the given role.

    These additions patch known Gemini CLI behavioural differences that
    would otherwise cause incorrect or failed pipeline runs. Each section
    is annotated with the specific issue it addresses.

    Returns an empty string for roles that have no Gemini-specific rules.
    """
    sections = []

    if role == "IMPLEMENTOR":
        # Issue 1: Gemini's tool execution layer misinterprets heredoc syntax
        # (cat <<'EOF' ... EOF), producing shell parse errors before the
        # command runs. Use printf for all multi-line file writes instead.
        # Discovered: user-service TM regression Run 1 (2026-03-23).
        # Model affected: gemini-3-flash-preview.
        #
        # Issue 2: Gemini's write_file tool is sandboxed to the launch cwd
        # (a per-invocation temp directory). Attempts to write files at
        # absolute paths outside that directory are rejected with:
        #   "Path not in workspace: ... resolves outside the allowed workspace"
        # Use run_shell_command with printf to write all files instead — shell
        # commands are not subject to the cwd sandbox.
        # Discovered: user-service TM regression Run 3 (2026-03-24).
        # Model affected: gemini-3-flash-preview.
        sections.append(
            "## File Writing Rules\n"
            "Always write files using run_shell_command with printf — NOT the write_file tool "
            "and NOT heredocs:\n"
            "  printf '%s' 'file content here' > /absolute/path/to/filename.go\n"
            "Do NOT use the write_file tool. It cannot access paths outside the workspace.\n"
            "Do NOT use cat <<'EOF' ... EOF syntax. It causes shell parse errors in this environment."
        )

    if not sections:
        return ""

    return "\n\n## Gemini Compatibility Notes\n\n" + "\n\n".join(sections) + "\n"
