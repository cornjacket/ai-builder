import importlib
import inspect

from agents.base import InternalAgent
from agents.context import AgentContext


def load_internal_agent(impl_path: str, ctx: AgentContext) -> InternalAgent:
    """Resolve a dotted class path (e.g. 'agents.tester.TesterAgent') and instantiate it.

    Classes that declare a `ctx` parameter in __init__ receive the AgentContext;
    context-free classes (TesterAgent, DocumenterAgent) are instantiated without it.
    """
    module_path, class_name = impl_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    if "ctx" in inspect.signature(cls.__init__).parameters:
        return cls(ctx=ctx)
    return cls()
