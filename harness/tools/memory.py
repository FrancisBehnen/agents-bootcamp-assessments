"""Long-term memory tools: save_note and read_notes.

There are two kinds of agent memory, and it's important not to mix them up:

- SHORT-TERM memory = the conversation so far (the messages list). LangGraph
  handles this with a *checkpointer* — you'll wire that up on day 2.
- LONG-TERM memory = facts that should survive across conversations, like
  "this customer prefers quiet appliances". That's what these tools do.

Here, long-term memory is just a JSON file on disk (`.agent_memory.json` in
the folder you run your agent from). Open the file after a chat and look
inside — being able to SEE your agent's memory makes it much less magical.
"""

import json
from pathlib import Path

from langchain.tools import tool

# The memory lives in the current working directory, so each assignment
# folder gets its own memory file. It's git-ignored.
_MEMORY_FILE = Path(".agent_memory.json")


def _load() -> list[str]:
    if _MEMORY_FILE.exists():
        return json.loads(_MEMORY_FILE.read_text())
    return []


@tool
def save_note(note: str) -> str:
    """Save a note to long-term memory, so it can be recalled in future conversations.

    Use this for durable facts worth remembering, e.g. "Customer's name is Sanne"
    or "Customer prefers quiet appliances (max 50 dB)".

    Args:
        note: One short, self-contained fact to remember.
    """
    notes = _load()
    notes.append(note)
    _MEMORY_FILE.write_text(json.dumps(notes, indent=2))
    return f"Saved. Memory now contains {len(notes)} note(s)."


@tool
def read_notes() -> str:
    """Read all notes from long-term memory.

    Use this at the start of a conversation to recall what you know about
    the customer from previous chats.
    """
    notes = _load()
    if not notes:
        return "Long-term memory is empty."
    return "Notes in long-term memory:\n" + "\n".join(f"- {n}" for n in notes)
