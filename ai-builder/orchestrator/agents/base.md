# agents/base.py

Defines the `InternalAgent` Protocol and re-exports `AgentResult` from
`agent_wrapper`.

## AgentResult

```python
@dataclass
class AgentResult:
    exit_code: int        # 0=success, 1=agent error, 2=timeout
    response: str         # full text response (OUTCOME:/HANDOFF: lines)
    tokens_in: int = 0
    tokens_out: int = 0
    tokens_cached: int = 0
```

Internal agents always return `tokens_in=tokens_out=tokens_cached=0` (no model
invoked). The orchestrator reads these fields when recording the execution log.

## InternalAgent Protocol

```python
@runtime_checkable
class InternalAgent(Protocol):
    def run(self, job_doc: Path, output_dir: Path, **kwargs) -> AgentResult:
        ...
```

`@runtime_checkable` enables `isinstance` checks. Signature conformance is not
verified at runtime — that requires mypy (see task `188227`).
