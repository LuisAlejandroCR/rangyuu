# test_onboard.py: la cámara a bordo. Sin calibración no puede hablar de metros, así que lo único
# que se le exige es distinguir "el suelo sigue igual" de "al frente hay otra cosa" — y no
# autorizar nunca por su cuenta.

import numpy as np
import pytest

from rangyuu.onboard import CLEAR, OBSTACLE, UNCERTAIN, ForwardClearance


def floor(value=140, height=120, width=80):
    return np.full((height, width), float(value), dtype=np.float32)


def test_an_even_floor_reads_clear():
    reading = ForwardClearance().look(floor())
    assert reading.state == CLEAR and not reading.degrades and reading.confidence > 0.5


def test_something_ahead_that_is_not_the_floor_reads_obstacle():
    frame = floor()
    frame[55:85, 25:60] = 30.0                    # un bulto oscuro en la franja de adelante
    reading = ForwardClearance().look(frame)
    assert reading.state == OBSTACLE and reading.degrades


def test_a_dark_shape_over_a_lit_floor_is_an_obstacle_not_darkness():
    frame = floor(150)
    frame[50:87, 22:64] = 12.0
    assert ForwardClearance().look(frame).state == OBSTACLE


def test_a_dark_scene_end_to_end_is_uncertain_not_blocked():
    assert ForwardClearance().look(floor(10)).state == UNCERTAIN


def test_a_mild_change_of_surface_is_uncertain_rather_than_free():
    frame = floor(140)
    frame[55:85, 25:60] = 125.0
    assert ForwardClearance().look(frame).state == UNCERTAIN


@pytest.mark.parametrize("bad", [np.zeros((8, 8), dtype=np.float32), np.zeros((4, 4, 3), dtype=np.float32)])
def test_a_frame_too_small_or_not_grayscale_is_refused(bad):
    with pytest.raises(ValueError):
        ForwardClearance().look(bad)


def test_thresholds_must_grow_from_uncertain_to_obstacle():
    with pytest.raises(ValueError):
        ForwardClearance(obstacle_contrast=5, uncertain_contrast=9)


def test_every_non_clear_reading_degrades():
    frame = floor()
    frame[55:85, 25:60] = 30.0
    assert ForwardClearance().look(frame).degrades
    assert ForwardClearance().look(floor(10)).degrades
    assert not ForwardClearance().look(floor()).degrades


# --- el filtro temporal: rápido para frenar, lento para volver a autorizar ---

from rangyuu.onboard import Clearance, ClearanceFilter


def reading(state, confidence=0.8):
    return Clearance(state, confidence, 10.0, 0.0)


def filtered(agree=4, dwell=1.2):
    clock = {"t": 0.0}
    return ClearanceFilter(agree=agree, dwell_s=dwell, clock=lambda: clock["t"]), clock


def test_a_worse_reading_lands_immediately():
    flt, clock = filtered()
    clock["t"] = 10.0
    assert flt.push(reading(OBSTACLE)) == OBSTACLE


def test_going_back_to_clear_needs_agreement_and_time():
    flt, clock = filtered(agree=4, dwell=1.2)
    flt.push(reading(OBSTACLE))
    for step in range(3):
        clock["t"] += 0.1
        assert flt.push(reading(CLEAR)) == OBSTACLE       # todavía no hay acuerdo suficiente
    clock["t"] += 2.0
    flt.push(reading(CLEAR))
    assert flt.push(reading(CLEAR)) == CLEAR


def test_one_stray_clear_frame_does_not_lift_a_stop():
    flt, clock = filtered()
    flt.push(reading(OBSTACLE))
    clock["t"] += 5.0
    assert flt.push(reading(CLEAR)) == OBSTACLE
    assert flt.push(reading(OBSTACLE)) == OBSTACLE


def test_the_filter_starts_uncertain_so_it_never_authorises_on_boot():
    flt, _ = filtered()
    assert flt.state == UNCERTAIN


@pytest.mark.parametrize("bad", [{"agree": 0}, {"dwell_s": -1}])
def test_invalid_filter_settings_are_refused(bad):
    with pytest.raises(ValueError):
        ClearanceFilter(**bad)
