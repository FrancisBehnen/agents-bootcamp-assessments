"""Run mystery-shopper scenario 13 through the Ultimate Agent supervisor.

Run it directly:
    python demo/scenario_13_demo.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
AGENT_FILE = (
    ROOT
    / "day-3"
    / "final-assignment-ultimate-agent"
    / "starter"
    / "main.py"
)

QUESTION = (
    "I recently had a problem with my washing machine from order ORD-1006. "
    "I want a similar washing machine. Can you recommend one for me?"
)


def load_supervisor():
    """Load the team's supervisor without duplicating its configuration."""
    sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location("ultimate_agent_main", AGENT_FILE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load agent from {AGENT_FILE}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.supervisor


def main() -> None:
    supervisor = load_supervisor()
    config = {"configurable": {"thread_id": f"scenario-13-demo-{uuid4().hex}"}}

    print(f"\n\033[1m🧑 Customer:\033[0m {QUESTION}\n")
    result = supervisor.invoke(
        {"messages": [{"role": "user", "content": QUESTION}]},
        config=config,
    )

    for message in result["messages"]:
        role = message.__class__.__name__.replace("Message", "")
        tool_calls = getattr(message, "tool_calls", None)
        if role == "AI" and tool_calls:
            for call in tool_calls:
                print(f"  \033[33m🔧 calling {call['name']}({call['args']})\033[0m")
        elif role == "Tool":
            print(f"  \033[36m↩️  {message.content}\033[0m")
        elif role == "AI" and message.content:
            print(f"\n\033[1;32m🤖 CoolShop:\033[0m {message.content}")


if __name__ == "__main__":
    main()