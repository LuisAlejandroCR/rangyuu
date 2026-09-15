"""B0 contract tests: source observation, safe policy, and HTTP boundaries."""

import hashlib
import hmac
import json
import threading
from http.server import HTTPServer
from pathlib import Path
from urllib import error, request

import pytest

from rangyuu.api import RingApiState, make_handler
from rangyuu.geometry import homography_dlt, project_point
from rangyuu.policy import Decision, cell_is_stale, decision_report
from rangyuu.ring import observation_from_event


FIXTURES = Path(__file__).parent / "fixtures" / "b0_events.json"


def _events():
    return json.loads(FIXTURES.read_text(encoding="utf-8"))


def _start_server(secret="test-secret"):
    server = HTTPServer(("127.0.0.1", 0), make_handler(RingApiState(secret)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{server.server_port}"


def _post(url, body, signature=None):
    raw = json.dumps(body, separators=(",", ":")).encode()
    headers = {"Content-Type": "application/json", "Content-Length": str(len(raw))}
    if signature is not None:
        headers["X-Signature"] = signature
    req = request.Request(url, raw, headers=headers, method="POST")
    try:
        with request.urlopen(req) as response:
            return response.status, json.loads(response.read())
    except error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def _signed_post(url, body, secret="test-secret"):
    raw = json.dumps(body, separators=(",", ":")).encode()
    signature = hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
    return _post(url, body, signature)


def test_bbox_bottom_center_projects_to_expected_grid_cell():
    homography = [[0.1, 0.0, 0.0], [0.0, 0.1, 0.0], [0.0, 0.0, 1.0]]
    bbox = _events()[0]["data"]["bounding_box"]
    bottom_center = ((bbox[0] + bbox[2]) / 2, bbox[3])
    floor_x, floor_y = project_point(homography, bottom_center)
    assert (floor_x, floor_y) == pytest.approx((2.0, 5.0))
    assert (int(floor_x), int(floor_y)) == (2, 5)


def test_fixture_free_and_occupied_observations_are_distinct():
    free, occupied, duplicate = _events()
    assert free["data"]["occupancy"] == "free"
    assert occupied["data"]["occupancy"] == "occupied"
    assert observation_from_event(free).confidence > observation_from_event(occupied).confidence - 0.02
    assert occupied["event_id"] == duplicate["event_id"]


def test_stale_occupancy_expires_at_declared_boundary():
    assert cell_is_stale(70, 100, 30)
    assert cell_is_stale(None, 100, 30)
    assert not cell_is_stale(71, 100, 30)


def test_invalid_calibration_is_rejected():
    with pytest.raises(ValueError, match="degenerate"):
        homography_dlt(
            [(0, 0), (1, 0), (2, 0), (3, 0)],
            [(0, 0), (1, 0), (2, 0), (3, 0)],
        )


def test_initial_rover_decision_is_safe_and_anchored():
    report = decision_report(device_id="", timestamp="", cells=[])
    assert report["decision"] == Decision.HOLD.value
    assert report["action"] != "TRAVERSE"
    assert report["evidence"]["cells"] == []


def test_signed_webhook_accepts_valid_event_and_rejects_invalid_event():
    server, base = _start_server()
    try:
        status, body = _signed_post(f"{base}/api/webhook/ring", _events()[0])
        assert status == 202
        assert body["accepted"] is True
        status, body = _signed_post(f"{base}/api/webhook/ring", {})
        assert status == 422
        assert "error" in body
    finally:
        server.shutdown()


def test_duplicate_webhook_is_idempotent():
    server, base = _start_server()
    try:
        event = _events()[1]
        assert _signed_post(f"{base}/api/webhook/ring", event)[0] == 202
        # A replay must not be applied as a second observation.  200/204 are
        # both acceptable idempotent acknowledgements.
        assert _signed_post(f"{base}/api/webhook/ring", event)[0] in (200, 204)
    finally:
        server.shutdown()
