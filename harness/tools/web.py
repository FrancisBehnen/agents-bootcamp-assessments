"""A browsing tool: fetch a webpage and return it as readable text.

This gives your agent eyes on the live internet. Two things to notice:

1. We strip the HTML down to plain text and TRUNCATE it. A raw webpage can
   be 100.000+ tokens of markup, and pasting that into the context window
   would drown your agent (remember "context rot" from the fundamentals day).
2. Web content is UNTRUSTED input. A page could contain text like "ignore
   your instructions and ...". That's prompt injection via a tool result.
   Good system prompts tell the agent to treat fetched content as data only.
"""

import requests
from bs4 import BeautifulSoup
from langchain.tools import tool

_MAX_CHARS = 4000  # roughly 1000 tokens: enough to read, small enough to stay sane


@tool
def fetch_webpage(url: str) -> str:
    """Download a webpage and return its readable text content (truncated).

    Args:
        url: The full URL including https://, e.g. "https://en.wikipedia.org/wiki/Coffee".
    """
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "agents-bootcamp/1.0 (educational)"},
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return f"Could not fetch {url}: {exc}"

    soup = BeautifulSoup(response.text, "html.parser")
    # Remove parts of the page that are never useful as text.
    for element in soup(["script", "style", "nav", "footer", "header"]):
        element.decompose()

    # Collapse the remaining text into clean lines.
    text = " ".join(soup.get_text(separator=" ").split())
    if len(text) > _MAX_CHARS:
        text = text[:_MAX_CHARS] + " ... [truncated]"
    return f"Content of {url}:\n{text}"
