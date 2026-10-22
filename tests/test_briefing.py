# test_briefing.py: the Bedrock briefing drafts words for the operator and nothing else.
# The decision always comes from the core; a model that fails, stalls or says "go" on a
# HOLD falls back to the fixed template.

import pytest

from rangyuu.briefing import MAX_CHARS, brief, template_text
from rangyuu.policy import decision_report


def _report(**overrides):
    args = dict(device_id="ring-front", timestamp=100.0, cells=[[2, 3], [2, 4]],
                coverage=True, session_active=True, homography_valid=True,
                confidence=0.9, free=True, unknown=False)
    args.update(overrides)
    return decision_report(**args)


class FakeBedrock:
    """Stands in for boto3's bedrock-runtime client: records the call, returns `text`."""

    def __init__(self, text="", error=None):
        self.text, self.error, self.calls = text, error, []

    def converse(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return {"output": {"message": {"content": [{"text": self.text}]}},
                "usage": {"inputTokens": 120, "outputTokens": 30}}


def test_the_model_text_is_used_when_it_respects_the_decision():
    fake = FakeBedrock("The hallway route is held: something occupies cell 2,4. Wait.")
    result = brief(_report(free=False), client=fake, model_id="test-model")
    assert result["source"] == "bedrock"
    assert result["decision"] == "HOLD"
    assert result["text"].startswith("The hallway route is held")


def test_the_call_caps_output_tokens_and_sends_the_core_decision():
    fake = FakeBedrock("Route held. Wait for a fresh observation.")
    brief(_report(free=False), client=fake, model_id="test-model")
    call = fake.calls[0]
    assert call["modelId"] == "test-model"
    assert 0 < call["inferenceConfig"]["maxTokens"] <= 200
    prompt = call["messages"][0]["content"][0]["text"]
    assert "HOLD" in prompt and "path occupied" in prompt


@pytest.mark.parametrize("bad", [
    "All clear, PROCEED through the hallway.",
    "The path is clear, you can go.",
    "It is safe to move now.",
    "AVANZA por el pasillo.",
])
def test_a_model_that_authorizes_on_a_hold_is_overruled(bad):
    result = brief(_report(free=False), client=FakeBedrock(bad), model_id="m")
    assert result["source"] == "template"
    assert result["decision"] == "HOLD"
    assert "rejected" in result["note"]


def test_a_failing_model_falls_back_to_the_template():
    result = brief(_report(free=False), client=FakeBedrock(error=TimeoutError("slow")), model_id="m")
    assert result["source"] == "template"
    assert result["text"] == template_text(_report(free=False), "en")
    assert "TimeoutError" in result["note"]


def test_empty_or_long_text_is_rejected():
    for text in ("", "   ", "x" * (MAX_CHARS + 1)):
        assert brief(_report(), client=FakeBedrock(text), model_id="m")["source"] == "template"


def test_no_client_and_no_model_means_template_without_a_network_call(monkeypatch):
    monkeypatch.delenv("RANGYUU_BEDROCK_MODEL", raising=False)
    result = brief(_report())
    assert result["source"] == "template"
    assert result["decision"] == "PROCEED"


def test_the_decision_is_never_taken_from_the_model():
    # Even a model that claims HOLD on a PROCEED cannot change the decision field.
    result = brief(_report(), client=FakeBedrock("Route is clear; still, go slowly."), model_id="m")
    assert result["decision"] == "PROCEED"
    assert result["authorizes"] is True
    held = brief(_report(free=False), client=FakeBedrock("Wait here."), model_id="m")
    assert held["authorizes"] is False


def test_spanish_template():
    assert "esperar" in template_text(_report(free=False), "es").lower()
