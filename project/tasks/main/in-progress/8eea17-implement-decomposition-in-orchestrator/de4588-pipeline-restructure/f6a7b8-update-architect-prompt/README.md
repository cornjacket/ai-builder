# Subtask: update-architect-prompt

| Field       | Value                                                                 |
|-------------|-----------------------------------------------------------------------|
| Status      | —                                                                     |
| Epic        | main                                                                  |
| Tags        | —                                                                     |
| Parent      | 8eea17-implement-decomposition-in-orchestrator/de4588-pipeline-restructure |
| Complexity  | —                                                                     |
| Stop-after  | false                                                                 |

## Description

Update roles/ARCHITECT.md to reflect that it fills named sections within
a task README (pointed to by current-job.txt), not a standalone document.

Decompose mode: fill ## Components and ## Suggested Tools
Design mode: fill ## Design, ## Acceptance Criteria, ## Suggested Tools

The prompt should explicitly state which sections to fill and leave
others untouched. Use updated outcome names:
  ARCHITECT_DECOMPOSITION_READY, ARCHITECT_DESIGN_READY,
  ARCHITECT_NEEDS_REVISION, ARCHITECT_NEED_HELP
