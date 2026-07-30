"""The bootcamp *harness*: shared helper code for all assignments.

"Harness" is a term you'll hear a lot this week: it's everything AROUND the
LLM that turns it into a useful system, such as the model configuration, the
tools, the memory, and the instructions. This package is a mini version of
that idea.

What lives here:
  - harness.llm      → get_llm(): a ready-to-use chat model
  - harness.data     → the mock webshop data (products, orders, FAQ)
  - harness.tools    → ready-made tools your agents can call

Typical usage in an assignment:

    from harness import get_llm
    from harness.tools import get_weather, calculator
"""

from harness.agent import create_agent
from harness.llm import get_llm

__all__ = ["create_agent", "get_llm"]
