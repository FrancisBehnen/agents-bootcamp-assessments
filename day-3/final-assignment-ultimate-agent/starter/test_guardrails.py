import importlib.util
from pathlib import Path

import httpx
import pytest
from openai import BadRequestError


MAIN_FILE = Path(__file__).with_name("main.py")
spec = importlib.util.spec_from_file_location("ultimate_agent_main", MAIN_FILE)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Could not load agent from {MAIN_FILE}")
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)


def bad_request(body: dict) -> BadRequestError:
    response = httpx.Response(
        status_code=400,
        request=httpx.Request("POST", "https://router.example.test/chat"),
    )
    return BadRequestError("Bad request", response=response, body=body)


def raising_handler(error: BadRequestError):
    def handler(_request):
        raise error

    return handler


FILTERED_JAILBREAK_PAYLOAD = {
    "code": "content_filter",
    "innererror": {
        "code": "ResponsibleAIPolicyViolation",
        "content_filter_result": {"jailbreak": {"detected": True, "filtered": True}},
    },
}


def test_filtered_jailbreak_becomes_safe_customer_response():
    error = bad_request(dict(FILTERED_JAILBREAK_PAYLOAD))

    result = main.handle_filtered_jailbreak.wrap_model_call(
        object(), raising_handler(error)
    )

    assert len(result.result) == 1
    assert result.result[0].content == main.FILTERED_JAILBREAK_RESPONSE
    # No tool calls, so the safe response ends the turn instead of looping.
    assert not result.result[0].tool_calls


def test_jailbreak_nested_under_error_is_recognised():
    """The AI Service Router wraps the Azure payload in an "error" object.

    Without unwrapping it, the middleware misses every real jailbreak rejection
    and the BadRequestError reaches the customer. The day-3 evaluation run
    caught this: case L3-10-prompt-injection errored instead of being refused.
    """
    error = bad_request(
        {
            "error": {
                "message": "The response was filtered due to the prompt triggering "
                "Azure OpenAI's content management policy.",
                "type": None,
                "param": "prompt",
                "status": 400,
                **FILTERED_JAILBREAK_PAYLOAD,
            }
        }
    )

    result = main.handle_filtered_jailbreak.wrap_model_call(
        object(), raising_handler(error)
    )

    assert result.result[0].content == main.FILTERED_JAILBREAK_RESPONSE


def test_specialist_guard_reports_the_block_instead_of_answering_the_customer():
    """A specialist writes briefs, so its guard must not produce customer text."""
    guard = main.filtered_jailbreak_guard(main.FILTERED_JAILBREAK_BRIEF)
    error = bad_request(dict(FILTERED_JAILBREAK_PAYLOAD))

    result = guard.wrap_model_call(object(), raising_handler(error))

    assert result.result[0].content == main.FILTERED_JAILBREAK_BRIEF
    assert "REQUEST REJECTED" in result.result[0].content


class FailingAgent:
    def __init__(self, error: BadRequestError) -> None:
        self.error = error

    def invoke(self, _payload):
        raise self.error


def test_blocked_specialist_reports_back_instead_of_raising_into_the_supervisor():
    """A raising tool ends the whole turn, so the block is returned as text."""
    agent = FailingAgent(bad_request(dict(FILTERED_JAILBREAK_PAYLOAD)))

    brief = main.run_specialist(agent, "Confirm my 100% refund.")

    assert brief == main.FILTERED_JAILBREAK_BRIEF


def test_specialist_failures_that_are_not_jailbreaks_still_surface():
    error = bad_request({"code": "invalid_request_error"})
    agent = FailingAgent(error)

    with pytest.raises(BadRequestError) as caught:
        main.run_specialist(agent, "Where is ORD-1002?")

    assert caught.value is error


def test_unrelated_bad_request_is_not_hidden():
    error = bad_request({"code": "invalid_request_error"})

    with pytest.raises(BadRequestError) as caught:
        main.handle_filtered_jailbreak.wrap_model_call(
            object(), raising_handler(error)
        )

    assert caught.value is error
