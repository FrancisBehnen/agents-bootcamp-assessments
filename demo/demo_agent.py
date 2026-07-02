"""A complete, runnable demo agent, used to record the README GIF.

Unlike the assignment starter files (which have TODO gaps for students to
fill), this one is finished and works out of the box. Its only job is to be a
short, pretty demonstration of the agent loop for the demo recording.

Run it directly:
    python demo/demo_agent.py

Record it as a GIF (see demo/README.md):
    vhs demo/agent-demo.tape
"""

from langchain.agents import create_agent

from harness import get_llm
from harness.tools import calculator, get_weather

SYSTEM_PROMPT = (
    "You are a friendly assistant. Always use your tools instead of guessing: "
    "use get_weather for weather questions and calculator for any math. "
    "Keep your final answer short and cheerful."
)

QUESTION = "What's the weather in Rotterdam, and what is 17.5% of 2840?"


def main() -> None:
    agent = create_agent(model=get_llm(), tools=[get_weather, calculator], system_prompt=SYSTEM_PROMPT)

    print(f"\n\033[1m🧑 You:\033[0m {QUESTION}\n")
    result = agent.invoke({"messages": [{"role": "user", "content": QUESTION}]})

    # Walk the message history so the recording SHOWS the loop: the agent
    # thinks, calls a tool, reads the result, and thinks again.
    for message in result["messages"]:
        role = message.__class__.__name__.replace("Message", "")
        tool_calls = getattr(message, "tool_calls", None)
        if role == "AI" and tool_calls:
            for call in tool_calls:
                print(f"  \033[33m🔧 calling {call['name']}({call['args']})\033[0m")
        elif role == "Tool":
            print(f"  \033[36m↩️  {message.content}\033[0m")
        elif role == "AI" and message.content:
            print(f"\n\033[1;32m🤖 Agent:\033[0m {message.content}")


if __name__ == "__main__":
    main()
