"""Agent construction helpers shared by the bootcamp assignments."""

from collections.abc import Sequence
from typing import Any

from langchain.agents import create_agent as _create_agent
from langchain.agents.middleware import AgentMiddleware, ModelRequest, wrap_model_call
from langchain_core.messages import SystemMessage


def _developer_message_middleware(message: str) -> AgentMiddleware:
    @wrap_model_call
    def inject_developer_message(request: ModelRequest, handler):
        developer_message = SystemMessage(content=message)
        return handler(
            request.override(messages=[developer_message, *request.messages])
        )

    return inject_developer_message


def create_agent(
    *args: Any,
    developer_message: str | None = None,
    middleware: Sequence[AgentMiddleware] = (),
    **kwargs: Any,
):
    """Create a LangChain agent with an optional recurring developer message."""
    if developer_message:
        middleware = (_developer_message_middleware(developer_message), *middleware)

    return _create_agent(*args, middleware=middleware, **kwargs)