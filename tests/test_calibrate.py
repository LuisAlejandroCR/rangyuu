# test_calibrate.py: calibration reports an error in centimetres, and a perfect fit on the
# four fitting points proves nothing — the held-out check is what has to be trusted.

import pytest

from rangyuu.calibrate import Calibration, Correspondence, calibrate, check_point, rectangle


def square(width=1.5, height=0.9):
    """A synthetic camera view of a measured rectangle: pixels chosen, floor measured."""
    pixels = [(100, 700), (380, 700), (330, 520), (150, 520)]
    return [Correspondence(pixel, floor, label)
            for pixel, floor, label in zip(pixels, rectangle(width, height), "abcd")]


def test_rectangle_is_measured_counter_clockwise_from_the_near_left_corner():
    assert rectangle(1.5, 0.9) == ((0.0, 0.0), (1.5, 0.0), (1.5, 0.9), (0.0, 0.9))


@pytest.mark.parametrize("bad", [(0, 1), (1, 0), (-1, 1)])
def test_a_rectangle_with_a_non_positive_side_is_refused(bad):
    with pytest.raises(ValueError):
        rectangle(*bad)


def test_the_four_fitting_points_land_on_their_measurement():
    calibration = calibrate(square())
    assert calibration.max_error_cm < 0.1
    assert set(calibration.as_dict()["per_point_cm"]) == set("abcd")


def test_fewer_than_four_correspondences_is_refused():
    with pytest.raises(ValueError):
        calibrate(square()[:3])


def test_a_held_out_point_is_what_actually_measures_the_calibration():
    calibration = calibrate(square())
    centre_pixel = (240, 610)
    error = check_point(calibration, centre_pixel, (0.75, 0.45))
    assert error >= 0.0
    assert check_point(calibration, (100, 700), (0.0, 0.0)) < 0.1


def test_error_summary_is_reported_in_centimetres_not_as_a_verdict():
    calibration = Calibration([[1, 0, 0], [0, 1, 0], [0, 0, 1]], (1.0, 3.0, 2.0), ("a", "b", "c"))
    assert calibration.mean_error_cm == 2.0 and calibration.max_error_cm == 3.0
