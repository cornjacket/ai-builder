# agents/loader.py

Provides `load_internal_agent` — resolves a dotted class path from machine JSON
and instantiates the corresponding agent class.

## load_internal_agent(impl_path, ctx)

**Input:** `impl_path: str` — dotted path such as `"agents.tester.TesterAgent"`;
`ctx: AgentContext` — orchestrator context for agents that need it.

**Output:** an instance satisfying `InternalAgent`.

**Behaviour:**
1. Splits `impl_path` at the last `.` to get `module_path` and `class_name`.
2. Calls `importlib.import_module(module_path)`.
3. Gets the class via `getattr`.
4. Inspects `__init__` — if the constructor declares a `ctx` parameter, calls
   `cls(ctx=ctx)`; otherwise calls `cls()`.

The `ctx` inspection avoids requiring context-free classes to accept an unused
argument while keeping the loader generic.

## Called from

`orchestrator.py` → `run_internal_agent` (constructs a fresh instance per call).
`tests/unit/test_agents.py` → `TestLoadInternalAgent` (verifies all `"impl"` paths
in `default.json` resolve and satisfy the Protocol).
