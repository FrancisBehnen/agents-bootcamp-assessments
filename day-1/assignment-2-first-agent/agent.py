"""Day 1 · Assignment 2 — Build your first agent.

An agent = an LLM in a LOOP with TOOLS and a GOAL. This morning YOU decided
the steps; now the LLM decides them. create_agent() gives you that loop for
free, so you can focus on the two things that actually shape an agent:

    PART A: the system prompt   (a tool is already wired — you ONLY edit the prompt)
    PART B: adding your own tool (write a new tool from scratch)

Run it (from this folder):
    python agent.py
"""

from langchain.agents import create_agent
from langchain.tools import tool

from harness import get_llm
from harness.tools import calculator, get_weather

# ===========================================================================
# PART B lives here — but do PART A first!
# ---------------------------------------------------------------------------
# A tool is just a normal Python function with the @tool decorator and a good
# docstring. The LLM reads the function name, the docstring and the argument
# names/types, and decides WHEN to call it. Your code decides WHAT it does.

# ✅ WORKED EXAMPLE — a complete, working tool. Read every line.
@tool
def count_words(text: str) -> str:
    """Count how many words are in a piece of text.

    Args:
        text: The text whose words should be counted.
    """
    number_of_words = len(text.split())
    return f"That text contains {number_of_words} words."


# TODO(you) PART B — write your OWN tool here, from scratch.
#
# Spec: a tool that converts an amount in euros to US dollars.
#       Use a fixed exchange rate of 1 EUR = 1.08 USD.
#
# Steps:
#   1. Copy the shape of count_words above (the @tool line, a def, a docstring).
#   2. Give it a clear name (e.g. eur_to_usd) and one typed argument (a number).
#   3. Write a docstring that tells the LLM exactly what it does — this is how
#      the model decides to use it, so make it clear!
#   4. Return a short, friendly string with the result.
#   5. Add it to the TOOLS list below (next to count_words).
#
# ... your tool goes here ...


# ===========================================================================
# PART A — the agent. Start here.
# ===========================================================================

# TODO(you) PART A: leave this as-is for now. get_weather and calculator are
# already wired up, so your agent can check the weather and do exact math.
# TODO(you) PART B: add count_words and your own new tool to this list.
TOOLS = [get_weather, calculator]


# TODO(you) PART A: write the system prompt — the agent's "job description".
# Cover at least:
#   - who the agent is and what it helps with
#   - that it should USE its tools instead of guessing (e.g. always use the
#     calculator for math, never do mental arithmetic)
#   - what to do when it CANNOT answer with the tools it has (be honest, don't
#     make things up)
SYSTEM_PROMPT = """REPLACE ME with your system prompt."""


def build_agent():
    # This one call builds the whole think -> tool -> think loop for you.
    return create_agent(
        model=get_llm(),
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
    )


# ===========================================================================
# Try it out
# ===========================================================================
# For PART A, this question needs BOTH the weather tool and the calculator.
# For PART B, change it to something that needs your new tool, e.g.
#   "How many words are in this sentence, and how much is 250 euros in dollars?"
QUESTION = "What's the weather in Rotterdam, and what is 17.5% of 2840?"

if __name__ == "__main__":
    agent = build_agent()

    print(f"QUESTION: {QUESTION}\n")
    result = agent.invoke({"messages": [{"role": "user", "content": QUESTION}]})

    # Print the whole conversation so you can SEE the loop: the agent thinks,
    # calls a tool, reads the result, and thinks again.
    for message in result["messages"]:
        message.pretty_print()

    print("\nNow find this run in https://smith.langchain.com and study the loop!")
