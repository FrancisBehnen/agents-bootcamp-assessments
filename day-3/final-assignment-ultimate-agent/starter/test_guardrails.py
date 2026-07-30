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


def test_filtered_jailbreak_becomes_safe_customer_response():
    error = bad_request(
        {
            "code": "content_filter",
            "innererror": {
                "code": "ResponsibleAIPolicyViolation",
                "content_filter_result": {
                    "jailbreak": {"detected": True, "filtered": True}
                },
            },
        }
    )

    result = main.handle_filtered_jailbreak.wrap_model_call(
        object(), raising_handler(error)
    )

    assert len(result.result) == 1
    assert result.result[0].content == main.FILTERED_JAILBREAK_RESPONSE
    assert "can't authorize refunds" in result.result[0].content


def test_unrelated_bad_request_is_not_hidden():
    error = bad_request({"code": "invalid_request_error"})

    with pytest.raises(BadRequestError) as caught:
        main.handle_filtered_jailbreak.wrap_model_call(
            object(), raising_handler(error)
        )

    assert caught.value is error
