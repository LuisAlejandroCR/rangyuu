# test_calibration_onboard.py: the B11 gate and its wiring into Site. The synthetic tests run
# today and prove the gate refuses an unmeasured or over-ceiling calibration and that the walking
# lane only writes to the map when it opens; the fixture test stays skipped, loudly, until somebody
# records the clip. Distinct from test_calibration_home.py, which guards the fixed camera.

import json

import numpy as np
import pytest

from rangyuu.onboard_calibration import (ERROR_CEILING_CM, NotMeasured, fit, held_out_error_cm,
                                         is_measured, load, verified_homography)
from rangyuu.runtime import LocalRuntime
from rangyuu.site import Site

IDENTITY = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

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


# --- the wiring: what the walking lane does with the gate's answer -------------------------

def onboard_site(**kwargs):
    """A site on the phone's lane. `requires_measured_calibration=False` keeps these tests about
    the map-writing gate, not the transit gate, which test_degradation_gates.py owns."""
    runtime = LocalRuntime("iphone-onboard", IDENTITY, cell_size=0.3, max_age=600.0,
                           stale_after=600.0)
    return Site(runtime, clock=lambda: 1000.0, requires_measured_calibration=False, **kwargs)


def two_frames():
    """A flat frame and the same frame with something in it: enough for the detector to fire."""
    first = np.full((120, 160), 40, dtype=np.float32)
    second = first.copy()
    second[30:90, 40:120] = 220.0
    return first, second


def test_the_shipped_template_leaves_the_lane_observing_and_not_writing():
    site = onboard_site()
    assert site.onboard_homography is None
    first, second = two_frames()
    site.observe_onboard(first)
    result = site.observe_onboard(second)
    assert result["written"] == 0
    assert "no está calibrado" in result["reason"]
    assert site.runtime.state.cells == {}


def test_a_measured_calibration_within_the_ceiling_opens_the_lane():
    site = onboard_site(onboard_calibration=SYNTHETIC)
    assert site.onboard_homography is not None
    first, second = two_frames()
    site.observe_onboard(first)
    result = site.observe_onboard(second)
    assert "reason" not in result
    assert result["written"] >= 1
    assert site.runtime.state.cells != {}


def test_a_calibration_over_the_ceiling_keeps_the_lane_shut():
    site = onboard_site(onboard_calibration=SYNTHETIC_OFF)
    assert site.onboard_homography is None
    first, second = two_frames()
    site.observe_onboard(first)
    assert site.observe_onboard(second)["written"] == 0


def test_a_half_filled_fixture_is_no_calibration_instead_of_a_crash():
    """The safe answer to a broken fixture is None, not an exception the caller must remember."""
    assert onboard_site(onboard_calibration={"status": "measured"}).onboard_homography is None


def test_the_measurement_bench_can_declare_itself_uncalibrated():
    """walk.py passes None on purpose: on an identity homography, writing cells invents them."""
    assert onboard_site(onboard_calibration=None).onboard_homography is None
