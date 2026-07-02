"""A safe calculator tool.

Why does an LLM need a calculator? Because LLMs predict text, they don't
compute. Ask one for 4382 * 1.21 and it will confidently give you a number
that is *almost* right. Tools fix this: let the LLM decide WHAT to calculate
and let real code do the calculating.

Note: we deliberately do NOT use Python's `eval()` here. `eval` executes
arbitrary code, and the expression comes (indirectly) from a user talking to
your agent. That's the "prompt injection" risk from the fundamentals day.
Instead we parse the expression and only allow harmless math operations.
"""

import ast
import operator

from langchain.tools import tool

# The only operations we allow. Anything else raises an error.
_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,   # unary minus, e.g. "-5"
    ast.UAdd: operator.pos,
}


def _safe_eval(node: ast.AST) -> float:
    """Recursively evaluate a parsed expression, allowing only basic math."""
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"Unsupported expression element: {ast.dump(node)}")


@tool
def calculator(expression: str) -> str:
    """Evaluate a math expression and return the exact result.

    Supports +, -, *, /, ** (power), % (modulo) and parentheses.

    Args:
        expression: The expression to evaluate, e.g. "1299 * 0.85" or "(23 + 7) / 3".
    """
    try:
        result = _safe_eval(ast.parse(expression, mode="eval"))
    except Exception:
        # A good tool returns a HELPFUL error the LLM can act on, instead of
        # crashing the whole agent. The model will read this and try again.
        return (
            f"Could not evaluate '{expression}'. Only numbers and the operators "
            "+ - * / ** % and parentheses are supported. Please rewrite the expression."
        )
    # Round floats to avoid noise like 156.99999999999997
    if isinstance(result, float):
        result = round(result, 6)
    return f"{expression} = {result}"
