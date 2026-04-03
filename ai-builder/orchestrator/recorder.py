"""
Record and replay support for the pipeline orchestrator.

Record mode: git-snapshots the regression workspace after each invocation and
writes a recording.json manifest at run end. AI response text is stored in
responses/inv-N-ROLE.txt so replay can serve the same response without calling
the AI.

Replay mode: loads the manifest, checks for prompt drift, and serves pre-recorded
AI responses in order. Non-AI handlers re-run normally.

Usage in orchestrator.py:
    import recorder as recorder_mod

    # Record
    recorder_mod.init(record_dir)
    sha = recorder_mod.commit(record_dir, n, role, outcome, response=text_or_none)
    recorder_mod.write_manifest(record_dir, invocations, ROLE_PROMPTS, REPO_ROOT)

    # Replay
    manifest = recorder_mod.load_manifest(replay_dir)
    drifted  = recorder_mod.check_prompt_drift(manifest, ROLE_PROMPTS, REPO_ROOT)
    queue    = recorder_mod.load_ai_responses(replay_dir, manifest)
    # queue is a list of (n, role, response_text) for AI invocations, in order
"""

import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Record mode
# ---------------------------------------------------------------------------

def init(
    record_dir: Path,
    branch: str | None = None,
    remote_url: str | None = None,
) -> None:
    """Initialize a git repo in record_dir if one does not already exist.

    Args:
        record_dir:  Root of the recording workspace.
        branch:      Orphan branch name to create (e.g. "user-service"). An orphan
                     branch has no parent commits and shares no history with other
                     branches in the same remote repo.
        remote_url:  Remote URL to add as 'origin' (e.g. the ai-builder-recordings
                     repo). Used by record.sh to push after the run completes.
    """
    record_dir.mkdir(parents=True, exist_ok=True)
    if (record_dir / ".git").exists():
        return
    _git(record_dir, ["init"])
    _git(record_dir, ["config", "user.email", "recorder@ai-builder"])
    _git(record_dir, ["config", "user.name", "ai-builder recorder"])
    if branch:
        _git(record_dir, ["checkout", "--orphan", branch])
    if remote_url:
        _git(record_dir, ["remote", "add", "origin", remote_url])
    suffix = f" (branch: {branch})" if branch else ""
    print(f"[recorder] Initialized recording repo in {record_dir}{suffix}")


def commit(
    record_dir: Path,
    n: int,
    role: str,
    outcome: str,
    response: str | None = None,
) -> str:
    """Stage all changes and commit. Returns the commit SHA.

    If response is provided (AI invocations only), it is written to
    responses/inv-{n:02d}-{role}.txt before staging so replay can serve
    it without re-calling the AI.

    Uses --allow-empty so handler invocations that produce no file changes
    (e.g. TESTER pass) still get a commit, keeping the invocation index
    in sync with the manifest.
    """
    if response is not None:
        resp_dir = record_dir / "responses"
        resp_dir.mkdir(exist_ok=True)
        (resp_dir / f"inv-{n:02d}-{role}.txt").write_text(response)

    _git(record_dir, ["add", "-A"])
    msg = f"inv-{n:02d} {role} {outcome}"
    _git(record_dir, ["commit", "--allow-empty", "-m", msg])
    return _git(record_dir, ["rev-parse", "HEAD"], capture=True).strip()


def write_manifest(
    record_dir: Path,
    invocations: list[dict],
    role_prompts: dict,
    repo_root: Path,
    task_hex_id: str | None = None,
) -> None:
    """Write recording.json manifest to record_dir.

    Args:
        record_dir:   Root of the recording git repo.
        invocations:  Ordered list of {n, role, outcome, commit, ai} dicts.
        role_prompts: ROLE_PROMPTS from orchestrator (role -> Path | None).
        repo_root:    Root of the ai-builder repo (for ai_builder_commit + relative paths).
        task_hex_id:  6-char hex ID of the top-level user task (e.g. "61857e").
                      When present, replay tooling passes this to new-user-task.sh
                      so all task directory names match the recording exactly.
    """
    try:
        ai_builder_commit = _git(repo_root, ["rev-parse", "HEAD"], capture=True).strip()
    except Exception:
        ai_builder_commit = "unknown"

    prompt_hashes: dict[str, str] = {}
    for role, prompt_path in role_prompts.items():
        if prompt_path is not None and prompt_path.exists():
            digest = hashlib.sha256(prompt_path.read_bytes()).hexdigest()
            try:
                key = str(prompt_path.relative_to(repo_root))
            except ValueError:
                key = str(prompt_path)
            prompt_hashes[key] = f"sha256:{digest}"

    manifest: dict = {
        "recorded_at": datetime.now().isoformat(),
        "ai_builder_commit": ai_builder_commit,
    }
    if task_hex_id:
        manifest["task_hex_id"] = task_hex_id
    manifest["prompt_hashes"] = prompt_hashes
    manifest["invocations"] = invocations
    manifest_path = record_dir / "recording.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"[recorder] Manifest written to {manifest_path}")


# ---------------------------------------------------------------------------
# Replay mode
# ---------------------------------------------------------------------------

def load_manifest(record_dir: Path) -> dict:
    """Load and return recording.json. Raises FileNotFoundError if absent."""
    manifest_path = record_dir / "recording.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No recording manifest found at {manifest_path}")
    return json.loads(manifest_path.read_text())


def check_prompt_drift(
    manifest: dict,
    role_prompts: dict,
    repo_root: Path,
) -> list[str]:
    """Return a list of prompt keys that changed since the recording was captured.

    An empty list means no drift — safe to replay. A non-empty list means one or
    more role prompts have changed and the recording may no longer be valid.
    Only prompts present in both the manifest and role_prompts are checked;
    new or removed prompts are not flagged.
    """
    drifted: list[str] = []
    stored = manifest.get("prompt_hashes", {})
    for role, prompt_path in role_prompts.items():
        if prompt_path is None or not prompt_path.exists():
            continue
        try:
            key = str(prompt_path.relative_to(repo_root))
        except ValueError:
            key = str(prompt_path)
        if key not in stored:
            continue
        current = "sha256:" + hashlib.sha256(prompt_path.read_bytes()).hexdigest()
        if current != stored[key]:
            drifted.append(key)
    return drifted


def load_ai_responses(
    record_dir: Path,
    manifest: dict,
) -> list[tuple[int, str, str]]:
    """Return an ordered list of (n, role, response_text) for AI invocations.

    Raises FileNotFoundError if a response file is missing from the recording.
    """
    responses: list[tuple[int, str, str]] = []
    for inv in manifest.get("invocations", []):
        if not inv.get("ai"):
            continue
        n, role = inv["n"], inv["role"]
        resp_file = record_dir / "responses" / f"inv-{n:02d}-{role}.txt"
        if not resp_file.exists():
            raise FileNotFoundError(
                f"Response file missing from recording: {resp_file}\n"
                f"Re-record with --record-to to regenerate."
            )
        responses.append((n, role, resp_file.read_text()))
    return responses


# ---------------------------------------------------------------------------
# Workspace restoration (replay)
# ---------------------------------------------------------------------------

def restore_output(
    record_dir: Path,
    n: int,
    exclude: list[str] | None = None,
) -> None:
    """Restore output/ from the recording commit at invocation N.

    Used during replay after serving a pre-recorded AI response for a role
    that writes to output/ (e.g. IMPLEMENTOR). Without this, TESTER would
    run against an empty output/ and fail — the recorded response text is
    parsed for OUTCOME/HANDOFF but does not re-execute the file writes.

    Only output/ is restored; target/ is left untouched because it contains
    fresh hex-prefixed task paths that differ between runs.

    Args:
        exclude: Git pathspecs to exclude (e.g. ["output/current-job.txt"]).
                 Orchestrator state files (current-job.txt, last-job.json,
                 execution.log, handoff-state.json) should always be excluded
                 so the live run's coordination state is not overwritten with
                 recording-era paths.
    """
    manifest = load_manifest(record_dir)
    sha = _sha_for_n(manifest, n)
    cmd = ["checkout", sha, "--", "output/"]
    if exclude:
        cmd += [f":(exclude){p}" for p in exclude]
    _git(record_dir, cmd)
    print(f"[recorder] Restored output/ from inv-{n:02d} ({sha[:8]})")


# ---------------------------------------------------------------------------
# Snapshot comparison
# ---------------------------------------------------------------------------

def diff_snapshot(
    record_dir: Path,
    at_n: int,
    against_n: int | None = None,
    exclude_paths: list[str] | None = None,
) -> str:
    """Diff the recording at invocation N against the working tree (or invocation M).

    Returns the unified diff as a string. An empty string means no differences.

    Args:
        record_dir:    Root of the recording git repo.
        at_n:          Invocation number to use as the base (resolved from manifest).
        against_n:     If given, diff inv-at_n against inv-against_n instead of the
                       working tree. Useful for inspecting what a single invocation
                       changed (pass N-1 and N to see just that invocation's writes).
        exclude_paths: Glob patterns to exclude from the diff (e.g. ["output/logs",
                       "output/execution.log"]). Uses git pathspec magic :(exclude).
    """
    manifest = load_manifest(record_dir)
    sha_at = _sha_for_n(manifest, at_n)

    cmd: list[str] = ["git", "diff", sha_at]
    if against_n is not None:
        sha_against = _sha_for_n(manifest, against_n)
        cmd = ["git", "diff", sha_at, sha_against]

    if exclude_paths:
        cmd += ["--"]
        cmd += [f":(exclude){p}" for p in exclude_paths]

    proc = subprocess.run(cmd, cwd=record_dir, capture_output=True, text=True, check=True)
    return proc.stdout


def _sha_for_n(manifest: dict, n: int) -> str:
    for inv in manifest.get("invocations", []):
        if inv["n"] == n:
            return inv["commit"]
    available = [inv["n"] for inv in manifest.get("invocations", [])]
    raise ValueError(f"Invocation {n} not found in recording manifest. Available: {available}")


# ---------------------------------------------------------------------------
# Internal
# ---------------------------------------------------------------------------

def _git(cwd: Path, args: list[str], capture: bool = False) -> str:
    proc = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout if capture else ""
