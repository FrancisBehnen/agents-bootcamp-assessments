"""🏆 Final Assignment — optional starter: the "agents as tools" pattern.

This is scaffolding, not a template. Use it, gut it, or ignore it — but if
you're staring at a blank editor at 10:30, start here.

The pattern: a specialist agent is wrapped in a @tool function, so the
supervisor can call an entire agent exactly like it calls a calculator.

              ┌────────────────────────────────────┐
              │            SUPERVISOR              │
              │  "who should handle this, and how  │
              │   do I combine their answers?"     │
              └────┬─────────────┬─────────────────┘
                   ▼             ▼
            ask_advisor    ask_order_desk     ... your agents here
            (specialist)    (specialist)

Run it:
    cd day-3/final-assignment-ultimate-agent/starter
    python main.py
"""

from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

from harness import get_llm
from harness.tools import (
    MEMORY_TOOLS,
    get_order_status,
    get_product_details,
    search_faq,
    search_products,
)

# ===========================================================================
# SPECIALIST 1: the product advisor
# ===========================================================================
# A specialist gets ONLY the tools and instructions for its own job. That
# focus is the entire point of splitting agents: small context, sharp
# behaviour. Note it has no memory and no order tools — not its job.
advisor_agent = create_agent(
    model=get_llm(),
    tools=[search_products, get_product_details],
    system_prompt=(
        "You are CoolShop's product advisor. You help customers choose "
        "products using your search and detail tools — never from memory. "
        "Be concrete and honest; if nothing fits, say so. "
        "TODO(team): make this prompt your own (use your day-2 work!)."
    ),
)


@tool
def ask_advisor(request: str) -> str:
    """Ask the product advisor to help with product choice or product advice.

    Args:
        request: The customer's need, with all relevant details you know
            (budget, use case, preferences).
    """
    # An agent invoked inside a tool — that's the whole trick. The supervisor
    # sees a normal tool; we run a full agent loop behind it.
    result = advisor_agent.invoke({"messages": [{"role": "user", "content": request}]})
    return result["messages"][-1].content


# ===========================================================================
# SPECIALIST 2: the order desk
# ===========================================================================
order_desk_agent = create_agent(
    model=get_llm(),
    tools=[get_order_status, search_faq],
    system_prompt=(
        "You are CoolShop's order desk. You answer questions about orders, "
        "delivery, returns and policies, always grounded in your tools. "
        "TODO(team): add your complaint-handling instructions here — or load "
        "them as a skill, like you did on day 2."
    ),
)


@tool
def ask_order_desk(request: str) -> str:
    """Ask the order desk about order status, delivery, returns or store policy.

    Args:
        request: The customer's question, including the order number if known.
    """
    result = order_desk_agent.invoke({"messages": [{"role": "user", "content": request}]})
    return result["messages"][-1].content


# ===========================================================================
# TODO(team): SPECIALIST 3, 4, ... — this is where YOUR ideas go.
# A complaints agent with the day-2 skills? A comparison agent? An agent
# with your self-written tool? (Requirement: at least one self-written tool
# somewhere in the system.)
# ===========================================================================


# ===========================================================================
# THE SUPERVISOR
# ===========================================================================
supervisor = create_agent(
    model=get_llm(),
    tools=[ask_advisor, ask_order_desk, *MEMORY_TOOLS],
    system_prompt=(
        "You are CoolShop's customer service coordinator. You talk to the "
        "customer; your specialists (available as tools) do the domain work. "
        "Delegate substantive questions to the right specialist and pass along "
        "ALL relevant details in your request — specialists cannot see the "
        "conversation, only what you send them. Combine their answers into "
        "one warm, clear reply.\n\n"
        "TODO(team): memory instructions (when to save/read notes), guardrails, "
        "escalation rules, tone of voice — you know the drill by now."
    ),
    checkpointer=InMemorySaver(),  # the supervisor holds the conversation memory
)

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "demo"}}
    print("Ultimate Agent (starter). Type 'quit' to stop.\n")
    while True:
        user_input = input("Customer: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break
        if not user_input:
            continue
        result = supervisor.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config,
        )
        print(f"\nCoolShop: {result['messages'][-1].content}\n")
