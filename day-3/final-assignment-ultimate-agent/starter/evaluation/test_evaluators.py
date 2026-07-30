"""Tests for the offline evaluators. No model calls, no network."""

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from evaluators import (
    AnswerOutcome,
    ToolCallCollector,
    evaluate_tool_use,
    extract_final_answer,
    judge_answer_outcome,
    supervisor_tool_names,
)


def delegating_run() -> list:
    """A supervisor turn that delegates once and then answers the customer."""
    return [
        HumanMessage(content="Where is my order ORD-1002?"),
        AIMessage(
            content="",
            tool_calls=[
                {"name": "ask_order_desk", "args": {"request": "..."}, "id": "call-1"}
            ],
        ),
        ToolMessage(content="VERIFIED ORDER FACTS: shipped", tool_call_id="call-1"),
        AIMessage(content="Your order is on its way."),
    ]


def test_final_answer_ignores_messages_that_only_request_tools():
    assert extract_final_answer(delegating_run()) == "Your order is on its way."


def test_tool_names_are_ordered_and_stop_at_the_final_answer():
    messages = delegating_run()
    messages.append(
        AIMessage(
            content="",
            tool_calls=[{"name": "save_note", "args": {}, "id": "call-2"}],
        )
    )

    assert supervisor_tool_names(messages) == ["ask_order_desk"]


def test_nested_specialist_tools_appear_in_the_reported_trace():
    result = evaluate_tool_use(
        delegating_run(),
        collected_tool_names=["ask_order_desk", "get_order_status"],
        expects_tool_call=True,
    )

    assert result.tool_called_before_answer is True
    assert result.tools_called == ["ask_order_desk", "get_order_status"]
    assert result.meets_expectation is True


def test_answer_without_any_tool_call_fails_a_case_that_expects_one():
    messages = [
        HumanMessage(content="Where is my order ORD-1002?"),
        AIMessage(content="It will arrive on Thursday."),
    ]

    result = evaluate_tool_use(messages, expects_tool_call=True)

    assert result.tool_called_before_answer is False
    assert result.tools_called == []
    assert result.meets_expectation is False


def test_case_without_an_expectation_is_reported_but_not_scored():
    result = evaluate_tool_use(delegating_run(), expects_tool_call=None)

    assert result.tool_called_before_answer is True
    assert result.meets_expectation is None


def test_collector_records_tool_names_in_start_order():
    collector = ToolCallCollector()

    collector.on_tool_start({"name": "ask_advisor"}, "{}")
    collector.on_tool_start({"name": "search_products"}, "{}")

    assert collector.tool_names == ["ask_advisor", "search_products"]


class RecordingJudge:
    def __init__(self, outcome: AnswerOutcome) -> None:
        self.outcome = outcome
        self.messages: list = []

    def invoke(self, messages, config=None):
        self.messages = messages
        return self.outcome


def test_judge_receives_the_question_and_the_answer():
    expected = AnswerOutcome(label="ANSWERED", rationale="Gives the status.", confidence=0.9)
    judge = RecordingJudge(expected)

    outcome = judge_answer_outcome(
        "Where is my order ORD-1002?", "It is with the delivery partner.", judge=judge
    )

    assert outcome is expected
    user_message = judge.messages[-1]["content"]
    assert "Where is my order ORD-1002?" in user_message
    assert "It is with the delivery partner." in user_message


def test_missing_answer_is_not_answered_without_calling_the_judge():
    judge = RecordingJudge(
        AnswerOutcome(label="ANSWERED", rationale="unused", confidence=1.0)
    )

    outcome = judge_answer_outcome("Where is my order?", "   ", judge=judge)

    assert outcome.label == "NOT_ANSWERED"
    assert judge.messages == []
