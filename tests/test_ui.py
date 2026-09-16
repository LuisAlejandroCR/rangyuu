# test_ui.py: the screen never contradicts the core. CUIDADO may only degrade a PROCEED,
# and no derived state may turn a refusal into an authorisation.

import pytest

from rangyuu.ui import AVANZA, CUIDADO, PARA, SIN_CERTEZA, to_screen


def report(decision="PROCEED", reason="clear high-confidence path"):
    return {"decision": decision, "reason": reason, "action": "TRAVERSE"}


def test_a_clean_proceed_is_avanza_with_a_human_reason():
    screen = to_screen(report())
    assert screen.state == AVANZA and screen.authorizes and screen.reason == "camino libre"


def test_hold_is_para_and_unknown_is_sin_certeza():
    assert to_screen(report("HOLD", "path occupied")).state == PARA
    assert to_screen(report("UNKNOWN", "trajectory unknown")).state == SIN_CERTEZA
    assert not to_screen(report("HOLD", "path occupied")).authorizes
    assert not to_screen(report("UNKNOWN", "cell stale")).authorizes


@pytest.mark.parametrize("kwargs", [{"confidence": 0.55}, {"age_fraction": 0.9},
                                    {"adjacent_occupied": True}])
def test_a_thin_margin_degrades_proceed_to_cuidado(kwargs):
    screen = to_screen(report(), **kwargs)
    assert screen.state == CUIDADO and screen.authorizes and screen.detail


def test_a_comfortable_margin_stays_avanza():
    assert to_screen(report(), confidence=0.95, age_fraction=0.1).state == AVANZA


def test_missing_inputs_never_invent_cuidado():
    assert to_screen(report()).state == AVANZA


@pytest.mark.parametrize("decision,reason", [("HOLD", "path occupied"), ("UNKNOWN", "cell stale")])
def test_cuidado_never_softens_a_refusal(decision, reason):
    screen = to_screen(report(decision, reason), confidence=0.51, age_fraction=0.99,
                       adjacent_occupied=True)
    assert screen.state in (PARA, SIN_CERTEZA) and not screen.authorizes


@pytest.mark.parametrize("onboard,expected", [("OBSTACLE", CUIDADO), ("UNCERTAIN", CUIDADO), ("CLEAR", AVANZA)])
def test_the_onboard_lane_degrades_but_never_stops_on_its_own(onboard, expected):
    """Medido: el detector a bordo acierta el 22 % de sus 'obstáculo'. Avisa, no frena."""
    screen = to_screen(report(), onboard=onboard)
    assert screen.state == expected
    if onboard != "CLEAR":
        assert screen.detail and screen.authorizes


def test_the_onboard_lane_cannot_lift_a_refusal():
    assert to_screen(report("HOLD", "path occupied"), onboard="CLEAR").state == PARA


def test_an_unmapped_reason_is_shown_as_is_rather_than_hidden():
    assert to_screen(report("HOLD", "something new upstream")).reason == "something new upstream"
