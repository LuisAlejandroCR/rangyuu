# test_calibration_onboard.py: the B11 gate. The synthetic tests run today and prove the gate
# refuses an unmeasured or over-ceiling calibration; the fixture tests stay skipped, loudly, until
# somebody records the clip. Distinct from test_calibration_home.py, which guards the fixed camera.

import json

import pytest

from rangyuu.onboard_calibration import (ERROR_CEILING_CM, NotMeasured, fit, held_out_error_cm,
                                         is_measured, load, verified_homography)

# A square metre of floor seen by a camera that happens to look straight down: pixel = 100 * metre.
# Synthetic on purpose — these tests are about the gate, not about any real lens.
SYNTHETIC = {
    "status": "measured",
    "marks": {"rectangle_m": {"width": 1.0, "depth": 1.0},
              "points": [{"label": "NL", "pixel": [0.0, 0.0], "floor_m": [0.0, 0.0]},
                         {"label": "NR", "pixel": [100.0, 0.0], "floor_m": [1.0, 0.0]},
                         {"label": "FR", "pixel": [100.0, 100.0], "floor_m": [1.0, 1.0]},
                         {"label": "FL", "pixel": [0.0, 100.0], "floor_m": [0.0, 1.0]}]},
    "held_out": {"tile_side_m": 0.25, "pixels": [[50.0, 25.0], [50.0, 50.0]]},
}

# The same fit, but the held-out points are claimed to be 0.30 m apart when the image puts them at
# 0.25 m: a 5 cm lie the fit residual cannot see, because these points never entered the fit.
SYNTHETIC_OFF = json.loads(json.dumps(SYNTHETIC))
SYNTHETIC_OFF["held_out"]["tile_side_m"] = 0.30


def unfilled():
    return json.loads(json.dumps(SYNTHETIC)) | {"status": "pending"}


# --- the gate, provable today -------------------------------------------------------------

def test_the_shipped_template_is_not_measured():
    assert is_measured(load()) is False


def test_an_unmeasured_fixture_yields_no_homography():
    assert verified_homography() is None


def test_fitting_an_unmeasured_fixture_raises_instead_of_guessing():
    with pytest.raises(NotMeasured):
        fit(unfilled())


def test_a_measured_fixture_within_the_ceiling_yields_a_homography():
    assert verified_homography(SYNTHETIC) is not None


def test_a_measured_fixture_over_the_ceiling_yields_no_homography():
    assert held_out_error_cm(SYNTHETIC_OFF) == 5.0
    assert verified_homography(SYNTHETIC_OFF) is None


def test_the_fit_residual_is_not_accepted_as_the_proof():
    """The fit closes on its own corners at ~0 cm while the held-out point is 5 cm out.

    This is Lesson 3 as an executable claim: if the residual were what opened the gate, this
    calibration would authorise, and the map would be wrong by 5 cm everywhere.
    """
    assert fit(SYNTHETIC_OFF).max_error_cm < 0.1
    assert verified_homography(SYNTHETIC_OFF) is None


def test_status_alone_does_not_make_a_fixture_measured():
    half = json.loads(json.dumps(SYNTHETIC))
    half["held_out"]["pixels"] = []
    assert is_measured(half) is False


def test_one_held_out_point_measures_nothing():
    lonely = json.loads(json.dumps(SYNTHETIC))
    lonely["held_out"]["pixels"] = [[50.0, 25.0]]
    with pytest.raises(NotMeasured):
        held_out_error_cm(lonely)


# --- the real footage, still missing ------------------------------------------------------

def test_the_recorded_clip_lands_under_the_declared_ceiling():
    data = load()
    if not is_measured(data):
        pytest.skip("B11 ⏳ pendiente: falta grabar el clip y anotar fixtures/iphone/"
                    "calibration_points.json (ver fixtures/iphone/MEDICIONES.md)")
    assert held_out_error_cm(data) <= ERROR_CEILING_CM
