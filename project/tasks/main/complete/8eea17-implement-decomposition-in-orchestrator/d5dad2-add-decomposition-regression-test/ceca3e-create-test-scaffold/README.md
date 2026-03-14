# Subtask: create-test-scaffold

| Field       | Value                                                                        |
|-------------|------------------------------------------------------------------------------|
| Status      | complete                                                                     |
| Epic        | main                                                                         |
| Tags        | —                                                                            |
| Parent      | 8eea17-implement-decomposition-in-orchestrator/d5dad2-add-decomposition-regression-test |
| Priority    | —                                                                            |
| Complexity  | —                                                                            |
| Stop-after  | false                                                                        |

## Description

Create the directory scaffold for the user-service regression test, mirroring
the fibonacci test layout:

```
tests/regression/user-service/
    gold/           # (empty placeholder — populated by write-gold-test-suite)
    work/
        .gitignore  # ignore pipeline-generated artifacts
    reset.sh        # recreates /tmp target repo, copies work/ artifacts into place
    README.md       # describes the test and how to run it
```

**`reset.sh` must:**
1. Create a fresh target repo directory under `/tmp/ai-builder-test-user-service/`
2. Run `target/setup-project.sh` and `target/init-claude-md.sh` on it
3. Create the `user-service` task in `in-progress/` within the target repo's task system
4. Copy `work/JOB-user-service.md` (produced by write-job-document-template) into the
   pipeline output directory

**`README.md` must describe:**
- What the test verifies (decompose → design → implement → test loop)
- Prerequisites (`claude` and `gemini` CLIs available)
- How to run: `reset.sh` then `orchestrator.py --target-repo /tmp/... --output-dir ...`
- How to verify: run the gold test suite against the output

## Notes

The target repo lives on `/tmp` to avoid accidental check-in of generated artifacts.
