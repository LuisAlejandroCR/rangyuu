# test_webapp.py: the HTTP boundary the screens use. Served over a real socket on an ephemeral
# port, so the routing, the status codes and the refusals are exercised, not mocked.

import json
import threading
import urllib.error
import urllib.request
from http.server import HTTPServer

import pytest

from rangyuu.serve import build_site
from rangyuu.webapp import make_handler


@pytest.fixture(scope="module")
def base_url():
    server = HTTPServer(("127.0.0.1", 0), make_handler(build_site()))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


def get(url, path):
    with urllib.request.urlopen(url + path, timeout=5) as response:
        return response.status, json.loads(response.read())


def post(url, path, payload):
    request = urllib.request.Request(url + path, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read())


@pytest.mark.parametrize("path", ["/api/space/now", "/api/space/map", "/api/sources",
                                  "/api/decisions", "/api/health"])
def test_every_read_endpoint_answers(base_url, path):
    status, payload = get(base_url, path)
    assert status == 200 and isinstance(payload, dict)


def test_the_main_screen_gets_a_state_a_reason_and_its_evidence(base_url):
    _, payload = get(base_url, "/api/space/now")
    assert payload["state"] in {"AVANZA", "CUIDADO", "PARA", "SIN CERTEZA"}
    assert payload["reason"] and "evidence" in payload
    assert payload["authorizes"] is (payload["state"] in {"AVANZA", "CUIDADO"})


def test_the_sources_screen_tells_the_truth_about_calibration(base_url):
    _, payload = get(base_url, "/api/sources")
    assert {"valid", "error_cm", "ceiling_cm", "reason"} <= set(payload["calibration"])
    assert {s["kind"] for s in payload["sources"]} == {"RING_INFRASTRUCTURE", "IPHONE_ONBOARD"}


def test_the_route_can_be_set_and_comes_back_evaluated(base_url):
    status, payload = post(base_url, "/api/space/route", {"cells": [[2, 0], [2, 1]]})
    assert status == 200 and payload["route"] == [[2, 0], [2, 1]]


def test_calibration_reports_the_error_and_refuses_to_store_a_bad_fit(base_url):
    square = {"points": [
        {"label": "a", "pixel": [0, 0], "floor_m": [0, 0]},
        {"label": "b", "pixel": [100, 0], "floor_m": [1, 0]},
        {"label": "c", "pixel": [100, 100], "floor_m": [1, 1]},
        {"label": "d", "pixel": [0, 100], "floor_m": [0, 1]}]}
    status, payload = post(base_url, "/api/space/calibrate", square)
    assert status == 200 and payload["accepted"] and payload["max_error_cm"] < 1.5

    status, payload = post(base_url, "/api/space/calibrate", {"points": square["points"][:3]})
    assert status == 422 and "cuatro puntos" in payload["error"]


def test_an_onboard_frame_is_accepted_and_answers_with_the_new_state(base_url):
    frame = {"width": 32, "height": 32, "gray": [40] * 1024}
    status, payload = post(base_url, "/api/space/observe", frame)
    assert status == 200 and payload["now"]["state"] in {"AVANZA", "CUIDADO", "PARA", "SIN CERTEZA"}
    assert payload["clearance"]["state"] in {"CLEAR", "OBSTACLE", "UNCERTAIN"}

    status, payload = post(base_url, "/api/space/observe", {"width": 32, "height": 32, "gray": [40] * 10})
    assert status == 422

    # Un frame demasiado pequeño no puede decir nada del camino, y lo dice en vez de inventar.
    status, payload = post(base_url, "/api/space/observe", {"width": 8, "height": 8, "gray": [40] * 64})
    assert status == 422


def test_changing_the_cell_size_rebuilds_the_grid_and_says_what_it_discarded(base_url):
    status, payload = post(base_url, "/api/space/config", {"cell_size_m": 0.5})
    assert status == 200 and payload["cell_size_m"] == 0.5 and payload["cleared"] >= 0

    _, after = get(base_url, "/api/space/map")
    assert after["cell_size_m"] == 0.5 and after["cells"] == []

    status, payload = post(base_url, "/api/space/config", {"cell_size_m": 99})
    assert status == 422 and "tamaño de celda" in payload["error"]


def test_unknown_paths_are_not_found_and_the_app_shell_is_served(base_url):
    with pytest.raises(urllib.error.HTTPError) as error:
        get(base_url, "/api/nope")
    assert error.value.code == 404

    with urllib.request.urlopen(base_url + "/", timeout=5) as response:
        assert response.status == 200 and b"Rangyuu" in response.read()


def test_traversal_outside_the_web_root_is_refused(base_url):
    with pytest.raises(urllib.error.HTTPError) as error:
        get(base_url, "/../pyproject.toml")
    assert error.value.code in (400, 404)
