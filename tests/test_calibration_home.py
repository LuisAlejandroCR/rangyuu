# test_calibration_home.py: the measured calibration, as a regression guard. Fits on the four
# taped corners and checks the result against tile joints that were NOT part of the fit, so
# the declared error in centimetres cannot silently drift.

import json
from math import hypot
from pathlib import Path

from rangyuu import Correspondence, calibrate, project_point

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "home" / "calibration_points.json"
DECLARED_ERROR_CM = 1.5  # measured 0.9 cm over 61 cm on 2026-09-15; this is the ceiling


def load():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def calibration():
    marks = load()["marks"]["points"]
    return calibrate([Correspondence(tuple(m["pixel"]), tuple(m["floor_m"]), m["label"]) for m in marks])


def test_the_four_taped_corners_fit_their_measurement():
    assert calibration().max_error_cm < 0.1


def test_tile_joints_left_out_of_the_fit_land_within_the_declared_error():
    data = load()["held_out"]
    homography = calibration().homography
    projected = [project_point(homography, tuple(p)) for p in data["pixels"]]
    span = hypot(projected[-1][0] - projected[0][0], projected[-1][1] - projected[0][1])
    expected = data["tile_side_m"] * (len(projected) - 1)
    assert abs(span - expected) * 100 <= DECLARED_ERROR_CM


def test_the_joints_stay_on_one_line_so_the_fit_is_not_skewed():
    homography = calibration().homography
    xs = [project_point(homography, tuple(p))[0] for p in load()["held_out"]["pixels"]]
    assert max(xs) - min(xs) < 0.03
