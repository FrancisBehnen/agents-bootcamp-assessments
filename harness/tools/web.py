"""A browsing tool: fetch a webpage and return it as readable Markdown.

This gives your agent eyes on the live internet. Two things to notice:

1. We strip the HTML down to plain text and TRUNCATE it. A raw webpage can
   be 100.000+ tokens of markup, and pasting that into the context window
   would drown your agent (remember "context rot" from the fundamentals day).
2. Web content is UNTRUSTED input. A page could contain text like "ignore
   your instructions and ...". That's prompt injection via a tool result.
   Good system prompts tell the agent to treat fetched content as data only.
"""

import shutil
import subprocess
from urllib.parse import urlparse

import requests
from langchain.tools import tool

_MAX_CHARS = 4000  # roughly 1000 tokens: enough to read, small enough to stay sane


@tool
def fetch_webpage(url: str) -> str:
    """Download a webpage and return its readable Markdown content (truncated).

    Args:
        url: The full URL including https://, e.g. "https://en.wikipedia.org/wiki/Coffee".
    """
    if urlparse(url).path.lower().endswith(".md"):
        try:
            response = requests.get(
                url,
                timeout=10,
                headers={"User-Agent": "agents-bootcamp/1.0 (educational)"},
            )
            response.raise_for_status()
            text = response.text
        except requests.RequestException as exc:
            return f"Could not fetch {url}: {exc}"
    else:
        if shutil.which("defuddle") is None:
            return (
                f"Could not fetch {url}: Defuddle is not installed. "
                "Install it with `npm install -g defuddle`."
            )
        try:
            result = subprocess.run(
                ["defuddle", "parse", url, "--md"],
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return f"Could not fetch {url}: Defuddle timed out after 15 seconds"
        if result.returncode != 0:
            error = result.stderr.strip() or "Defuddle could not parse the page"
            return f"Could not fetch {url}: {error}"
        text = result.stdout.strip()

    if len(text) > _MAX_CHARS:
        text = text[:_MAX_CHARS] + " ... [truncated]"
    return f"Content of {url}:\n{text}"
