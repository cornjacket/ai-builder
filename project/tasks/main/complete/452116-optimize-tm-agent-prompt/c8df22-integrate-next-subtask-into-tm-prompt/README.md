# Task: integrate-next-subtask-into-tm-prompt

| Field       | Value                               |
|-------------|-------------------------------------|
| Status | complete |
| Epic        | main                                |
| Tags        | —                                   |
| Parent      | 452116-optimize-tm-agent-prompt     |
| Priority    | —                                   |
| Complexity  | atomic                              |
| Stop-after  | false                               |
| Last-task   | true                                |

## Goal

Replace the fragile list-parse approach in the TM prompt with a call to
`next-subtask.sh`, and update the available tools list in the prompt.

## Context

`next-subtask.sh` is implemented in `a77e9b`. The TM prompt in
`ai-builder/orchestrator/orchestrator.py` (`build_prompt()`) currently
instructs the TM agent to identify the next subtask using `list-tasks.sh`
and construct the path manually. This subtask replaces that instruction with
a direct call to `next-subtask.sh`.

## Design

In `build_prompt()`, the `TESTER_TESTS_PASS` branch (step 4), replace:
```
- Identify the next incomplete subtask using list-tasks.sh
- Point the pipeline at it:
    {PM_SCRIPTS_DIR}/set-current-job.sh ...
```
with:
```
- Get the next incomplete subtask:
    NEXT=$(project/tasks/scripts/next-subtask.sh --epic {EPIC} --folder in-progress --parent <parent-id-name>)
- Point the pipeline at it:
    {PM_SCRIPTS_DIR}/set-current-job.sh --output-dir {output_dir} $NEXT
```

Also add `next-subtask.sh` to the Available Tools list in both TM prompt
branches.

## Acceptance Criteria

1. TM prompt no longer instructs the agent to use `list-tasks.sh` to find
   the next subtask
2. TM prompt instructs the agent to call `next-subtask.sh` and use its output
3. `next-subtask.sh` appears in the Available Tools list in both TM prompt
   branches
4. User-service regression test still passes end-to-end after the change

## Suggested Tools

```bash
# Run regression test to verify
bash tests/regression/user-service/reset.sh
python3 ai-builder/orchestrator/orchestrator.py \
    --target-repo sandbox/user-service-target \
    --output-dir  sandbox/user-service-output \
    --epic        main
cd tests/regression/user-service/gold && go test -tags regression ./...
```

## Notes

_None._
