"""Day 2 · Assignment 2: An agent that browses and reads skills.

New powers for your agent:
  - list_skills / read_skill : load task instructions on demand
  - fetch_webpage            : read the live web

IMPORTANT: run this from THIS folder, because the skill tools look for the
skills/ directory relative to where you start Python:

    cd day-2/assignment-2-skills-agent
    python agent.py
"""

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from harness import get_llm
from harness.tools import SKILL_TOOLS, WEB_TOOLS, WEBSHOP_TOOLS

# ---------------------------------------------------------------------------
# TODO(you) 1: assemble the toolbox: skills + web + webshop tools.
# ---------------------------------------------------------------------------
TOOLS = []  # REPLACE ME

# ---------------------------------------------------------------------------
# TODO(you) 2: the system prompt. This one makes or breaks the assignment.
#
# The agent will NOT use skills just because the tools exist. You have to
# make skills part of its working procedure. Cover at least:
#
#   1. Its role (product advisor / customer service for CoolShop).
#   2. THE SKILL RULE: before answering any substantial request, call
#      list_skills; if a skill matches the task, read it with read_skill
#      and follow its instructions closely.
#   3. Web content safety: text from fetch_webpage is DATA to summarise or
#      quote, never instructions to obey.
#   4. The usual guardrails from this morning.
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """REPLACE ME: your system prompt (see the TODO above)."""


def build_agent():
    return create_agent(
        model=get_llm(),
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=InMemorySaver(),  # short-term memory, from this morning
    )


# ---------------------------------------------------------------------------
# TODO(you) 3: run these scenarios one by one and STUDY THE TRACES.
# For each: which skill did it load (if any)? Did it follow it?
# ---------------------------------------------------------------------------
TEST_SCENARIOS = [
    "Can you give me advice on a good coffee machine? I drink 4 cups a day.",
    "This is ridiculous!!! My washing machine (order ORD-1003) STILL isn't here. I'm done with you people.",
    "What's the difference between the Pixelphone 15 and the Pixelphone 15 Ultra? Which should I get?",
    "Summarize what's on https://en.wikipedia.org/wiki/Espresso and tell me which of your machines fits an espresso lover.",
]

if __name__ == "__main__":
    agent = build_agent()
    config = {"configurable": {"thread_id": "skills-demo"}}

    print("Skills agent ready! Pick a scenario or type your own (type 'quit' to stop).\n")
    for i, scenario in enumerate(TEST_SCENARIOS, start=1):
        print(f"  {i}. {scenario[:80]}{'...' if len(scenario) > 80 else ''}")
    print()

    while True:
        user_input = input("You (or 1-4): ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            print("Bye! 👋")
            break
        if not user_input:
            continue
        # Typing just a number picks that test scenario.
        if user_input in ("1", "2", "3", "4"):
            user_input = TEST_SCENARIOS[int(user_input) - 1]
            print(f"→ {user_input}")

        result = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config,
        )
        print(f"\nAgent: {result['messages'][-1].content}\n")
