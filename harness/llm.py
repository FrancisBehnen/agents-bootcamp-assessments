"""One helper to get a configured LLM anywhere in the bootcamp.

We do NOT call OpenAI directly. Instead every call goes through Coolblue's
**AI Service Router**, an OpenAI-compatible endpoint owned by the Virtual
Agents Platform team that adds failover, shared quota and central auth. For
your code the difference is tiny: it's the same OpenAI interface, just
pointed at a different URL with one extra header.

Why a helper?
1. Convenience: you write `get_llm()` instead of repeating the router
   config in every file.
2. Flexibility: the model is chosen by BOOTCAMP_MODEL in your .env, so the
   whole class can switch models without touching code.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load the .env in the repo root, no matter which folder you run from.
_REPO_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(_REPO_ROOT / ".env")

# Default model. Must be a fully-pinned ID the router supports (see the
# supported-models list from the trainers). gpt-4.1-mini is fast + cheap and
# handles tool calling well, which makes it perfect for learning.
_DEFAULT_MODEL = "gpt-4.1-mini-2025-04-14"


def _require(var: str) -> str:
    """Read a required env var, or raise a friendly, actionable error."""
    value = os.getenv(var)
    if not value:
        raise RuntimeError(
            f"Environment variable {var} is not set.\n"
            f"Copy .env.example to .env and fill in the router details you "
            f"received from the trainers, then run `python check_setup.py`."
        )
    return value


def get_llm(model: str | None = None, temperature: float = 0.0):
    """Return a ready-to-use chat model, wired to the AI Service Router.

    Args:
        model: Optional override, e.g. "gpt-4.1-2025-04-14". If omitted, the
            BOOTCAMP_MODEL from your .env is used.
        temperature: How "creative" the model is. 0.0 = as predictable as
            possible (good for tool-calling agents!), 1.0 = more varied.
            You met this parameter on the LLM Fundamentals day.

    Example:
        >>> llm = get_llm()
        >>> llm.invoke("Say hi!").content
        'Hi!'
    """
    chosen = model or os.getenv("BOOTCAMP_MODEL", _DEFAULT_MODEL)

    # This is the whole router integration. Compare it with a plain OpenAI
    # setup: only base_url + the "client" header are new. Everything else,
    # including tools, agents, and streaming, works exactly as in the
    # LangChain docs.
    return ChatOpenAI(
        model=chosen,
        temperature=temperature,
        base_url=_require("AI_SERVICE_ROUTER_BASE_URL"),
        api_key=_require("AI_SERVICE_ROUTER_API_KEY"),
        # The router REQUIRES a "client" header telling it which team is
        # calling (for quota + auth). Forget this and you get "401 Invalid client".
        default_headers={"client": _require("AI_SERVICE_ROUTER_CLIENT")},
    )
