from langchain_core.tools import tool


@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression using Python operators (+, -, *, /, **)."""
    allowed = {"__builtins__": {}}
    try:
        return str(eval(expression, allowed, {}))
    except Exception as e:
        return f"Error evaluating '{expression}': {e}"
