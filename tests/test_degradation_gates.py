# test_degradation_gates.py: la puerta entre observar y autorizar. Comprueba que una
# homografía ajustada pero no medida contra un punto conocido nunca autoriza, que recalibrar
# borra la medición anterior, y que el sitio real sí autoriza con sus 0,9 cm medidos.
# Se distingue de test_core.py (tabla de decisión pura) y de test_spatial.py (mapa y celdas).

import time

import pytest

from rangyuu.calibrate import Correspondence, calibrate
from rangyuu.runtime import LocalRuntime
from rangyuu.serve import MEASURED_ERROR_CM, build_site
from rangyuu.site import Site
from rangyuu.webapp import _calibrate

IDENTITY = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
ROUTE = [(2, 0), (2, 1)]
# Cuatro esquinas de un rectángulo medido: el ajuste cierra sobre ellas con error ~0.
SQUARE = [((0, 0), (0.0, 0.0)), ((100, 0), (1.0, 0.0)),
          ((100, 100), (1.0, 1.0)), ((0, 100), (0.0, 1.0))]


def fitted():
    """Una calibración ajustada: cierra sobre sus propias esquinas y no prueba nada más."""
    return calibrate([Correspondence(pixel, floor, f"p{i}")
                      for i, (pixel, floor) in enumerate(SQUARE)])


def site(**kwargs):
    """Un sitio con la ruta observada libre y el feed vivo: solo falta la calibración."""
    clock = {"t": 1000.0}
    runtime = LocalRuntime("cam-1", IDENTITY, cell_size=1.0, max_age=30.0, stale_after=30.0)
    value = Site(runtime, clock=lambda: clock["t"], **kwargs)
    value.set_route(ROUTE)
    runtime.mark_free(ROUTE, now=clock["t"])
    runtime.last_frame_at = clock["t"]
    return value


# -- la puerta: ajustar no es verificar --------------------------------------


def test_a_fitted_but_unmeasured_calibration_observes_but_never_authorises():
    screen = site(calibration=fitted()).now()

    assert screen["decision"] == "HOLD"
    assert screen["authorizes"] is False
    assert screen["reason"] == "calibración no válida"
    # La evidencia sigue anclada: se pierde la autoridad, no el rastro.
    assert [tuple(c) for c in screen["evidence"]["cells"]] == ROUTE


def test_the_fit_residual_is_never_accepted_as_the_proof():
    # El error del propio ajuste es ~0 y aun así no habilita nada.
    value = site(calibration=fitted())

    assert value.calibration.max_error_cm < 0.1
    assert value.calibration_is_verified() is False
    assert value._calibration()["valid"] is False
    assert value._calibration()["measured"] is False


def test_a_measured_error_within_the_ceiling_authorises():
    screen = site(calibration=fitted(), measured_error_cm=0.9, error_ceiling_cm=1.5).now()

    assert screen["decision"] == "PROCEED"
    assert screen["authorizes"] is True


def test_a_measured_error_beyond_the_ceiling_does_not_authorise():
    value = site(calibration=fitted(), measured_error_cm=2.4, error_ceiling_cm=1.5)

    assert value.calibration_is_verified() is False
    assert value.now()["authorizes"] is False
    assert value._calibration()["reason"] == "requiere recalibración"


def test_an_uncalibrated_site_never_authorises():
    assert site().now()["authorizes"] is False


def test_the_walk_bench_is_the_only_lane_exempt_and_says_so():
    # El carril de a bordo mide el detector, no autoriza tránsito; la exención es explícita.
    assert site(requires_measured_calibration=False).now()["authorizes"] is True
    assert site().requires_measured_calibration is True


# -- la puerta: recalibrar borra la medición anterior -------------------------


def test_recalibrating_drops_the_previous_measurement_and_the_authority():
    value = site(calibration=fitted(), measured_error_cm=0.9, error_ceiling_cm=1.5)
    assert value.now()["authorizes"] is True

    payload = _calibrate(value, {"points": [{"pixel": list(pixel), "floor_m": list(floor)}
                                            for pixel, floor in SQUARE]})

    assert payload["accepted"] is True          # la matriz nueva se guarda
    assert payload["measured"] is False         # pero su error no está medido
    assert payload["authorizes"] is False
    assert value.now()["authorizes"] is False


def test_a_calibration_over_the_ceiling_is_not_stored_at_all():
    value = site(calibration=fitted(), measured_error_cm=0.9)
    with pytest.raises(ValueError):
        _calibrate(value, {"points": [{"pixel": [0, 0], "floor_m": [0, 0]}]})
    assert value.now()["authorizes"] is True    # un intento inválido no degrada lo que ya había


# -- el sitio real: la puerta está abierta porque hay una medición ------------


def test_the_shipped_site_authorises_because_its_error_was_measured():
    value = build_site()

    assert value.measured_error_cm == MEASURED_ERROR_CM == 0.9
    assert value.measured_error_cm <= value.error_ceiling_cm
    assert value.calibration_is_verified() is True
    assert value.now()["authorizes"] is True


def test_the_shipped_site_stops_authorising_the_moment_the_measurement_is_withdrawn():
    value = build_site()
    value.measured_error_cm = None

    screen = value.now()
    assert screen["decision"] == "HOLD" and screen["authorizes"] is False
    assert time.time() - value.runtime.last_frame_at < value.runtime.stale_after
