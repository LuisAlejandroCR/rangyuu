# briefing.py: Amazon Bedrock drafts a short operator briefing for a decision the core
# already made. Asynchronous lane only: the decision field is copied from the core, never
# from the model, and any reply that fails, runs long or sounds like "go" on a HOLD is
# replaced by a fixed template. Run `python -m rangyuu.briefing` for a live call.

import json
import os
import re
import sys
import time

MAX_CHARS = 280
MAX_TOKENS = 120   # a briefing is two sentences; never reserve the model's full quota

# Words that grant permission. On anything but PROCEED, a reply containing one is rejected,
# even when the model meant "not clear": failing closed costs a template, not a collision.
_AUTHORIZING = re.compile(
    r"\b(proceed|clear|safe to|go ahead|you can go|can pass|avanza|adelante|despejad[oa]|"
    r"puede[s]? pasar|libre)\b", re.IGNORECASE)

_TEMPLATES = {
    "en": {"PROCEED": "Route authorized by the core: {reason}. Supervise the crossing.",
           "HOLD": "Route held: {reason}. Wait; nothing authorizes transit.",
           "UNKNOWN": "Route uncertain: {reason}. Wait for fresh evidence."},
    "es": {"PROCEED": "Ruta autorizada por el núcleo: {reason}. Supervise el cruce.",
           "HOLD": "Ruta detenida: {reason}. Hay que esperar; nada autoriza el paso.",
           "UNKNOWN": "Ruta sin certeza: {reason}. Hay que esperar evidencia fresca."},
}

_SYSTEM = (
    "You write one or two short sentences for a caregiver supervising a mobility device. "
    "You are given a decision that was already made by a safety system; you never change it, "
    "never second-guess it and never add facts that are not in the input. "
    "If the decision is HOLD or UNKNOWN, tell them to wait and why, and never use the words "
    "proceed, clear, safe, go ahead, avanza, adelante, despejado or libre. "
    f"At most {MAX_CHARS} characters. Plain text, no markdown. Language: {{lang}}."
)


def template_text(report: dict, lang: str = "en") -> str:
    table = _TEMPLATES.get(lang, _TEMPLATES["en"])
    decision = str(report.get("decision", "UNKNOWN"))
    return table.get(decision, table["UNKNOWN"]).format(reason=report.get("reason", "no reason"))


def _prompt(report: dict) -> str:
    evidence = report.get("evidence") or {}
    facts = {"decision": report.get("decision"), "reason": report.get("reason"),
             "device": evidence.get("device_id"), "observed_at": evidence.get("timestamp"),
             "cells": evidence.get("cells")}
    return "Decision already made by the core:\n" + json.dumps(facts, ensure_ascii=False)


def _rejection(text: str, decision: str):
    if not text.strip():
        return "empty reply"
    if len(text) > MAX_CHARS:
        return f"reply over {MAX_CHARS} characters"
    if decision != "PROCEED" and _AUTHORIZING.search(text):
        return "reply sounds like permission on a non-PROCEED decision"
    return None


def _default_client():
    import boto3
    from botocore.config import Config
    return boto3.client("bedrock-runtime", config=Config(
        retries={"max_attempts": 2, "mode": "adaptive"}, connect_timeout=3, read_timeout=10))


def brief(report: dict, *, lang: str = "en", client=None, model_id=None) -> dict:
    """Return {decision, authorizes, text, source, note}. `source` is "bedrock" or "template"."""
    decision = str(report.get("decision", "UNKNOWN"))
    result = {"decision": decision, "authorizes": decision == "PROCEED",
              "text": template_text(report, lang), "source": "template", "note": ""}
    model_id = model_id or os.environ.get("RANGYUU_BEDROCK_MODEL")
    if not model_id:
        result["note"] = "RANGYUU_BEDROCK_MODEL not set"
        return result
    try:
        client = client or _default_client()
        started = time.perf_counter()
        response = client.converse(
            modelId=model_id,
            system=[{"text": _SYSTEM.format(lang="Spanish" if lang == "es" else "English")}],
            messages=[{"role": "user", "content": [{"text": _prompt(report)}]}],
            inferenceConfig={"maxTokens": MAX_TOKENS, "temperature": 0.2},
        )
        elapsed_ms = (time.perf_counter() - started) * 1000
        text = "".join(block.get("text", "")
                       for block in response["output"]["message"]["content"]).strip()
    except Exception as exc:   # any failure of the side lane leaves the template in place
        result["note"] = f"bedrock unavailable: {type(exc).__name__}"
        return result
    rejected = _rejection(text, decision)
    if rejected:
        result["note"] = f"model reply rejected: {rejected}"
        return result
    usage = response.get("usage") or {}
    result.update(text=text, source="bedrock",
                  note=f"{model_id}, {elapsed_ms:.0f} ms, "
                       f"{usage.get('inputTokens', '?')} in / {usage.get('outputTokens', '?')} out")
    return result


def main(argv=None) -> int:
    from rangyuu.policy import decision_report
    args = list(sys.argv[1:] if argv is None else argv)
    lang = "es" if "--es" in args else "en"
    cases = {
        "PROCEED": dict(free=True, confidence=0.9),
        "HOLD": dict(free=False, confidence=0.9),
        "UNKNOWN": dict(free=True, confidence=0.3),
    }
    for name, overrides in cases.items():
        report = decision_report(device_id="playground-cam", timestamp=100.0, cells=[[2, 3], [2, 4]],
                                 coverage=True, session_active=True, homography_valid=True,
                                 unknown=False, **overrides)
        out = brief(report, lang=lang)
        print(f"{name:8} [{out['source']}] {out['text']}\n         {out['note']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
