"""Strict HTTP boundary for Ring observations and rover decisions."""
from datetime import datetime, timezone
import json
from http.server import BaseHTTPRequestHandler

from .ring import observation_from_event, verify_hmac
from .spatial import SpatialState

MAX_BODY = 1_048_576


class RingApiState:
    def __init__(self, secret, *, calibrations=None, max_age=30):
        self.secret = secret
        self.spatial = SpatialState(max_age=max_age)
        self.seen = set()
        for device, homography in (calibrations or {}).items():
            self.spatial.calibrate(device, homography)

    def register(self, event):
        normalized = _normalize_event(event)
        event_id = normalized["event_id"]
        if event_id in self.seen:
            return False, False
        mapped = self.spatial.ingest(normalized)
        self.seen.add(event_id)
        return True, mapped


def make_handler(state):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, status, payload):
            body = json.dumps(payload, separators=(",", ":")).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _payload(self):
            if not state.secret:
                self._send(503, {"error": "authentication unavailable"}); return None
            if self.headers.get("Transfer-Encoding"):
                self._send(411, {"error": "content length required"}); return None
            if self.headers.get("Content-Type", "").split(";", 1)[0].lower() != "application/json":
                self._send(415, {"error": "json required"}); return None
            try:
                length = int(self.headers.get("Content-Length", "-1"))
            except ValueError:
                self._send(400, {"error": "invalid content length"}); return None
            if length < 0:
                self._send(411, {"error": "content length required"}); return None
            if length > MAX_BODY:
                self._send(413, {"error": "payload too large"}); return None
            raw = self.rfile.read(length)
            if len(raw) != length:
                self._send(400, {"error": "truncated body"}); return None
            if not verify_hmac(raw, self.headers.get("X-Signature", ""), state.secret):
                self._send(401, {"error": "invalid signature"}); return None
            try:
                value = json.loads(raw)
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._send(400, {"error": "invalid json"}); return None
            if not isinstance(value, dict):
                self._send(400, {"error": "json object required"}); return None
            return value

        def do_GET(self):
            if self.path.split("?", 1)[0] == "/health":
                self._send(200, {"status": "ok"})
            else:
                self._send(404, {"error": "not found"})

        def do_POST(self):
            path = self.path.split("?", 1)[0]
            if path not in {"/api/webhook/ring", "/api/rover/can-traverse"}:
                self._send(404, {"error": "not found"}); return
            value = self._payload()
            if value is None:
                return
            if path == "/api/webhook/ring":
                try:
                    accepted, mapped = state.register(value)
                except (KeyError, TypeError, ValueError):
                    self._send(422, {"error": "invalid observation"}); return
                self._send(202 if accepted else 200, {"accepted": True, "duplicate": not accepted, "mapped": mapped})
                return
            try:
                report = state.spatial.evaluate_trajectory(value.get("device_id"), _timestamp(value.get("timestamp")), value.get("trajectory"))
            except (TypeError, ValueError):
                self._send(422, {"error": "invalid trajectory"}); return
            report["authorizes"] = report["decision"] == "PROCEED"
            self._send(200, report)

        def log_message(self, *_args):
            return
    return Handler


def _normalize_event(event):
    observation = observation_from_event(event)
    event_id = event.get("event_id") or event.get("id")
    if not isinstance(event_id, str) or not event_id.strip() or observation.bbox is None:
        raise ValueError("event id and bounding box are required")
    x1, y1, x2, y2 = (float(value) for value in observation.bbox)
    if x2 < x1 or y2 < y1:
        raise ValueError("invalid bounding box")
    data = event.get("data", event)
    occupancy = data.get("occupancy")
    if occupancy not in {"free", "occupied"}:
        occupancy = "occupied" if observation.kind in {"person", "person_detected", "motion_detected", "vehicle"} else None
    if occupancy is None:
        raise ValueError("occupancy is required")
    return {
        "event_id": event_id,
        "device_id": observation.device_id,
        "timestamp": _timestamp(observation.timestamp),
        "bounding_box": [x1, y1, x2 - x1, y2 - y1],
        "confidence": observation.confidence,
        "kind": "path_clear" if occupancy == "free" else "person",
        "source": "ring",
    }


def _timestamp(value):
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str) or not value.strip():
        raise ValueError("timestamp is required")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return (parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)).timestamp()
