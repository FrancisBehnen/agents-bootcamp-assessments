"""FAQ / store-policy search tool.

This is a *very* simple retrieval system: it scores each FAQ entry by how
many keywords match the question. Real systems use embeddings for this (you
learned about those in LLM Fundamentals, "a numeric representation of
meaning"). The interface to the agent is the same either way: question in,
relevant text out. This is RAG in miniature.
"""

from langchain.tools import tool

from harness.data import FAQ


@tool
def search_faq(question: str) -> str:
    """Search the store's FAQ and policies (returns, delivery, warranty, payment, ...).

    Use this whenever a customer asks about rules or procedures, so your
    answer is based on real policy instead of guesswork.

    Args:
        question: The customer's question, e.g. "how do returns work?".
    """
    text = question.lower()

    # Score every FAQ entry: +1 for each keyword that appears in the question.
    scored = []
    for entry in FAQ:
        score = sum(1 for keyword in entry["keywords"] if keyword in text)
        if score > 0:
            scored.append((score, entry))

    if not scored:
        return (
            "No FAQ entry matched. Topics covered: returns, delivery, payment "
            "methods, warranty, store pickup, installation, cancellations, VAT."
        )

    # Return the top 2 matches: enough context, without flooding the agent.
    scored.sort(key=lambda pair: pair[0], reverse=True)
    results = []
    for _score, entry in scored[:2]:
        results.append(f"Q: {entry['question']}\nA: {entry['answer']}")
    return "\n\n".join(results)
