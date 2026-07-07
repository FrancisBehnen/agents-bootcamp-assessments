"""Day 1 · Assignment 1: Build your first workflow.

A workflow = fixed steps, decided by YOU in code. The LLM fills in each step
but never chooses what happens next:

    customer message -> classify -> answer_<category> -> polish -> done

The whole graph is ALREADY built and wired for you. Your only job is to write
the prompts: the parts marked TODO(you). Two answer prompts are given as
worked examples, so copy their style for the ones you write.

Run it (from this folder):
    python workflow.py
"""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from harness import get_llm

llm = get_llm()


# ---------------------------------------------------------------------------
# The STATE: a shared "clipboard" that travels through the workflow. Each node
# reads from it and writes new fields to it. (You don't need to touch this.)
# ---------------------------------------------------------------------------
class WorkflowState(TypedDict):
    customer_message: str  # filled in at the start
    category: str          # filled in by classify
    draft_answer: str      # filled in by one of the answer nodes
    final_answer: str      # filled in by polish


# ===========================================================================
# THE NODES: each one is a single LLM call. YOU write the prompts.
# ===========================================================================

def classify(state: WorkflowState) -> dict:
    """Decide what the message is about: 'product', 'order' or 'general'."""

    # TODO(you) 1: write the classification prompt.
    # Make the model answer with EXACTLY one word: product, order or general.
    # Tips: list the three labels and what each means, show the message, and
    # end with something like "Reply with only the label, nothing else."
    prompt = f"""
    REPLACE ME with your classification prompt.

    Customer message: {state["customer_message"]}
    """

    category = llm.invoke(prompt).content.strip().lower()
    # Safety net: if the model returns something unexpected, default to general
    # instead of crashing. (Check your traces: does this ever trigger?)
    if category not in ("product", "order", "general"):
        category = "general"
    return {"category": category}


def answer_product(state: WorkflowState) -> dict:
    """Draft an answer for a PRODUCT question.  ✅ WORKED EXAMPLE, read me!"""
    prompt = f"""You are a product expert at the webshop CoolShop.
Draft a short, helpful answer to this product question. If you don't know a
specific fact (like exact price or stock), say the customer can check the
product page, and never invent details.

Customer message: {state["customer_message"]}"""
    return {"draft_answer": llm.invoke(prompt).content}


def answer_order(state: WorkflowState) -> dict:
    """Draft an answer for an ORDER question."""

    # TODO(you) 2: write this prompt yourself, in the same style as
    # answer_product above. Think about what's different for order questions:
    # we can't actually look up the order yet (that's this afternoon's agent!),
    # so what CAN the model helpfully say, and what should it NOT promise?
    prompt = f"""
    REPLACE ME with your order-question prompt.

    Customer message: {state["customer_message"]}
    """
    return {"draft_answer": llm.invoke(prompt).content}


def answer_general(state: WorkflowState) -> dict:
    """Draft an answer for anything else.  ✅ WORKED EXAMPLE, read me!"""
    prompt = f"""You are a friendly customer service employee at CoolShop.
Draft a short answer to this message. If you can't help with the request, say
so honestly and point the customer to customerservice@coolshop.example.

Customer message: {state["customer_message"]}"""
    return {"draft_answer": llm.invoke(prompt).content}


def polish(state: WorkflowState) -> dict:
    """Rewrite the draft answer in CoolShop's tone of voice."""

    # TODO(you) 3: write a prompt that rewrites state["draft_answer"] to be:
    #   - warm and personal, but professional
    #   - at most ~4 sentences
    #   - ending with one friendly closing line
    prompt = f"""
    REPLACE ME with your polishing prompt.

    Draft answer to rewrite: {state["draft_answer"]}
    """
    return {"final_answer": llm.invoke(prompt).content}


# ===========================================================================
# THE GRAPH: already wired for you. You don't need to change anything below.
# (But do read it: this same node/edge structure powers every agent this week.)
# ===========================================================================

def route_by_category(state: WorkflowState) -> str:
    """After classify runs, send the message to the matching answer node."""
    return {
        "product": "answer_product",
        "order": "answer_order",
        "general": "answer_general",
    }[state["category"]]


def build_workflow():
    builder = StateGraph(WorkflowState)

    builder.add_node("classify", classify)
    builder.add_node("answer_product", answer_product)
    builder.add_node("answer_order", answer_order)
    builder.add_node("answer_general", answer_general)
    builder.add_node("polish", polish)

    builder.add_edge(START, "classify")
    # A conditional edge: after classify, jump to whichever node
    # route_by_category returns.
    builder.add_conditional_edges(
        "classify",
        route_by_category,
        ["answer_product", "answer_order", "answer_general"],
    )
    # Every answer node flows into polish, and polish ends the workflow.
    builder.add_edge("answer_product", "polish")
    builder.add_edge("answer_order", "polish")
    builder.add_edge("answer_general", "polish")
    builder.add_edge("polish", END)

    return builder.compile()


# ===========================================================================
# Try it out
# ===========================================================================
TEST_MESSAGES = [
    "Is the Aurora Book Pro 14 good enough for photo editing?",
    "Where is my order ORD-1003?? It was supposed to arrive yesterday!",
    "Do you also sell gift cards?",
]

if __name__ == "__main__":
    workflow = build_workflow()

    for message in TEST_MESSAGES:
        print("=" * 70)
        print(f"CUSTOMER: {message}\n")
        result = workflow.invoke({"customer_message": message})
        print(f"CATEGORY: {result['category']}")
        print(f"ANSWER:   {result['final_answer']}\n")

    print("=" * 70)
    print("Now open https://eu.smith.langchain.com and inspect the three traces!")
