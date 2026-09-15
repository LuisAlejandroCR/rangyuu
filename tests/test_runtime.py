# test_runtime.py: the critical loop. The decisive one is the network cut — when frames stop
# arriving, the runtime must degrade to the safe action instead of holding the last reading.
# Also proves inference is local: every socket is poisoned while a frame is processed.

import socket

import numpy as np
import pytest

from rangyuu.detect import MotionDetector
from rangyuu.runtime import LocalRuntime

IDENTITY = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
TRAJECTORY = [[2, 2], [3, 2]]


def runtime(**kwargs):
    return LocalRuntime("cam-1", IDENTITY, cell_size=1.0, max_age=5.0, stale_after=2.0, **kwargs)


def empty(height=240, width=320, value=40):
    return np.full((height, width), value, dtype=np.float32)


def moving(height=240, width=320):
    frame = empty(height, width)
    frame[80:200, 100:180] = 220.0
    return frame


def test_a_quiet_scene_writes_nothing():
    run = runtime()
    run.on_frame(empty(), now=100.0)
    assert run.on_frame(empty(), now=100.5)["detections"] == 0


def test_movement_is_detected_locally_and_becomes_an_occupied_cell():
    run = runtime()
    run.on_frame(empty(), now=100.0)
    result = run.on_frame(moving(), now=100.5)
    assert result["detections"] >= 1 and result["written"] >= 1
    assert result["inference_ms"] >= 0.0


def test_inference_opens_no_socket(monkeypatch):
    def forbidden(*_args, **_kwargs):
        raise AssertionError("the critical loop must not touch the network")

    run = runtime()
    run.on_frame(empty(), now=100.0)
    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    run.on_frame(moving(), now=100.5)


def test_the_network_cut_stops_authorizing_instead_of_holding_the_last_reading():
    run = runtime()
    run.on_frame(empty(), now=100.0)
    run.mark_free(TRAJECTORY, now=100.0)
    live = run.can_traverse(TRAJECTORY, now=100.5)
    assert live["decision"] == "PROCEED" and live["authorizes"]

    # frames stop arriving: the feed is gone, nothing else changes
    cut = run.can_traverse(TRAJECTORY, now=103.0)
    assert not cut["authorizes"] and cut["decision"] == "UNKNOWN"
    assert "feed stale" in cut["reason"]


def test_a_cold_runtime_never_authorizes():
    assert not runtime().can_traverse(TRAJECTORY, now=1.0)["authorizes"]


def test_the_budget_reports_milliseconds_per_stage():
    run = runtime()
    run.on_frame(empty(), now=100.0, decode_ms=3.0)
    run.on_frame(moving(), now=100.5, decode_ms=3.0)
    budget = run.budget.as_dict()
    assert budget["frames"] == 2 and budget["decode_ms"] == 3.0
    assert budget["inference_ms"] > 0 and budget["total_ms"] >= budget["inference_ms"]


@pytest.mark.parametrize("bad", [{"threshold": 0}, {"decay": 0}, {"decay": 2}, {"downscale": 0}])
def test_invalid_detector_settings_are_refused(bad):
    with pytest.raises(ValueError):
        MotionDetector(**bad)
