"""Ready-made tools for your agents.

A *tool* is nothing more than a Python function with a good description.
The `@tool` decorator (from LangChain) turns the function into something an
LLM can understand: the function name, the docstring and the argument types
are shown to the model, and the model decides WHEN to call it. Your code
decides WHAT the tool actually does.

Every file in this folder is short and heavily commented, so read them! They
are your examples for writing your own tools later this week.

Import individual tools:

    from harness.tools import get_weather, calculator

Or grab a themed bundle:

    from harness.tools import BASIC_TOOLS, WEBSHOP_TOOLS
"""

from harness.tools.calculator import calculator
from harness.tools.faq import search_faq
from harness.tools.memory import read_notes, save_note
from harness.tools.orders import get_order_status
from harness.tools.products import get_product_details, search_products
from harness.tools.skills import list_skills, read_skill
from harness.tools.weather import get_weather
from harness.tools.web import fetch_webpage

# Themed bundles, matched to the assignments:
BASIC_TOOLS = [get_weather, calculator]                                # day 1
WEBSHOP_TOOLS = [search_products, get_product_details,                 # day 2+
                 get_order_status, search_faq]
MEMORY_TOOLS = [save_note, read_notes]                                 # day 2
SKILL_TOOLS = [list_skills, read_skill]                                # day 2
WEB_TOOLS = [fetch_webpage]                                            # day 2+

__all__ = [
    "get_weather",
    "calculator",
    "search_products",
    "get_product_details",
    "get_order_status",
    "search_faq",
    "save_note",
    "read_notes",
    "list_skills",
    "read_skill",
    "fetch_webpage",
    "BASIC_TOOLS",
    "WEBSHOP_TOOLS",
    "MEMORY_TOOLS",
    "SKILL_TOOLS",
    "WEB_TOOLS",
]
