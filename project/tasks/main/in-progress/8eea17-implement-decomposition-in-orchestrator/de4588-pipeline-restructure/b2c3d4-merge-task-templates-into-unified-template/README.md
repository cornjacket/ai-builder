# Subtask: merge-task-templates-into-unified-template

| Field       | Value                                                                 |
|-------------|-----------------------------------------------------------------------|
| Status      | —                                                                     |
| Epic        | main                                                                  |
| Tags        | —                                                                     |
| Parent      | 8eea17-implement-decomposition-in-orchestrator/de4588-pipeline-restructure |
| Complexity  | —                                                                     |
| Stop-after  | false                                                                 |

## Description

Merge task-template.md and subtask-template.md into a single unified
template that includes all pipeline sections. Unused sections are left
with placeholder text; the pipeline fills in what is relevant.

Sections in the unified template:
- Standard task metadata (Status, Epic, Tags, Parent, Priority,
  Complexity, Stop-after)
- ## Goal
- ## Context
- ## Components  ← filled by ARCHITECT in decompose mode
- ## Design      ← filled by ARCHITECT in design mode
- ## Acceptance Criteria  ← filled by ARCHITECT
- ## Suggested Tools      ← filled by ARCHITECT
- ## Subtasks (with markers)
- ## Notes

Update both project/tasks/scripts/ and target/project/tasks/scripts/.
Update new-task.sh if it references the old template files.
