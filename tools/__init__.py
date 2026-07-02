import os
import inspect
import importlib.util
from langchain_core.tools import BaseTool


def _make_safe(tool):
    # Langchain has built-in tool error handling
    tool.handle_tool_error = True
    return tool


def discover_tools():
    tools = []
    tools_dir = os.path.dirname(os.path.abspath(__file__))

    for fname in sorted(os.listdir(tools_dir)):
        if not fname.endswith(".py") or fname.startswith("__"):
            continue

        module_path = os.path.join(tools_dir, fname)
        module_name = fname[:-3]

        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for name, obj in inspect.getmembers(module):
            if isinstance(obj, BaseTool):
                func = getattr(obj, "func", obj._run)
                if not obj.description:
                    raise ValueError(
                        f"Tool '{name}' in {fname} is missing a docstring "
                        f"(docstring -> tool description)"
                    )
                sig = inspect.signature(func)
                typed = [
                    p
                    for p in sig.parameters.values()
                    if p.name not in ("self", "cls")
                    and p.annotation != inspect.Parameter.empty
                ]
                if not typed:
                    raise ValueError(
                        f"Tool '{name}' in {fname} has no type hints on its parameters"
                    )
                tools.append(_make_safe(obj))

    return tools
