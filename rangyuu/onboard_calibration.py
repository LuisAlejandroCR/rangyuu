# onboard_calibration.py: turns the phone's tape-measured marks into a homography the walking lane
# may actually write with. Mirrors the site gate: a matrix that only closes on its own four corners
# is fitted, not verified, and this module refuses to hand it over until a held-out point says so.

import json
from math import hypot
from pathlib import Path

from .calibrate import Correspondence, calibrate, check_point
from .geometry import project_point

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "iphone" / "calibration_points.json"
ERROR_CEILING_CM = 1.5  # same ceiling as the fixed camera; B8 owns the number


class NotMeasured(Exception):
    """Raised when the fixture is still the unfilled template."""


def load(path=FIXTURE) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def is_measured(data) -> bool:
    """True only when somebody filled the template in and said so explicitly."""
    if data.get("status") != "measured":
        return False
    points = data.get("marks", {}).get("points", [])
    if len(points) < 4 or any(p.get("pixel") is None or p.get("floor_m") is None for p in points):
        return False
    held = data.get("held_out", {})
    return bool(held.get("pixels")) and held.get("tile_side_m") is not None


def correspondences(data) -> list:
    return [Correspondence(tuple(p["pixel"]), tuple(p["floor_m"]), p["label"])
            for p in data["marks"]["points"]]


def fit(data):
    """The homography and its fit residual. The residual is ~0 by construction: it proves nothing."""
    if not is_measured(data):
        raise NotMeasured("fixtures/iphone/calibration_points.json is still the empty template")
    return calibrate(correspondences(data))


def held_out_error_cm(data) -> float:
    """The honest number: how far the held-out span lands from its tape measurement.

    The reserved points sit a known distance apart on one line. Projecting them and comparing the
    span against that distance uses nothing the fit ever saw.
    """
    calibration = fit(data)
    held = data["held_out"]
    projected = [project_point(calibration.homography, tuple(p)) for p in held["pixels"]]
    if len(projected) < 2:
        raise NotMeasured("need at least two held-out points to measure anything")
    span = hypot(projected[-1][0] - projected[0][0], projected[-1][1] - projected[0][1])
    expected = held["tile_side_m"] * (len(projected) - 1)
    return round(abs(span - expected) * 100.0, 1)


def verified_homography(data=None, *, ceiling_cm=ERROR_CEILING_CM):
    """The matrix the walking lane may write with, or None.

    None is the safe answer and the default one: an uncalibrated source that writes to the map puts
    cells in the wrong place, which is worse than not writing at all.
    """
    data = load() if data is None else data
    if not is_measured(data):
        return None
    return fit(data).homography if held_out_error_cm(data) <= ceiling_cm else None
