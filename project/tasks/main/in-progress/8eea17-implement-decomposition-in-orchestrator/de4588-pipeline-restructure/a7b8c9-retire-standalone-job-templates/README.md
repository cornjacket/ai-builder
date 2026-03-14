# Subtask: retire-standalone-job-templates

| Field       | Value                                                                 |
|-------------|-----------------------------------------------------------------------|
| Status      | —                                                                     |
| Epic        | main                                                                  |
| Tags        | —                                                                     |
| Parent      | 8eea17-implement-decomposition-in-orchestrator/de4588-pipeline-restructure |
| Complexity  | —                                                                     |
| Stop-after  | false                                                                 |

## Description

Remove JOB-service-build.md and JOB-component-design.md from
ai-builder/orchestrator/. Their section formats are now embedded in the
unified task template.

Update orchestrator.md to reflect that job documents are task READMEs,
not files in the output dir. Update any references to these templates in
other docs (routing.md, decomposition.md, open-questions.md).

JOB-TEMPLATE.md (legacy non-TM mode) may be retained for now — evaluate
whether it is still needed once the unified template is in place.
