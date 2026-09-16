# test_app_e2e.py: the app in a real browser. It proves the memorable moment of the demo —
# the screen refusing to authorise — and skips cleanly where playwright is not installed,
# so the core suite never depends on a browser.

import threading
import time
from http.server import HTTPServer

import numpy as np
import pytest

from rangyuu.serve import build_site
from rangyuu.spatial import CellObservation
from rangyuu.webapp import make_handler

playwright_api = pytest.importorskip("playwright.sync_api")


@pytest.fixture(scope="module")
def app():
    site = build_site()
    server = HTTPServer(("127.0.0.1", 0), make_handler(site))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield site, f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


@pytest.fixture(scope="module")
def page(app):
    with playwright_api.sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as error:                      # no browser installed in this environment
            pytest.skip(f"chromium no disponible: {error}")
        page = browser.new_page(viewport={"width": 390, "height": 844})
        page.goto(app[1], wait_until="networkidle")
        yield page
        browser.close()


def state_of(page, expected=None, timeout=8000):
    """Espera a que la pantalla llegue al estado esperado, en vez de dormir un rato fijo:
    con la máquina cargada, una espera fija convierte una prueba correcta en intermitente."""
    page.click(".tabs button[data-goto='ahora']")
    if expected is None:
        page.wait_for_timeout(300)
        return page.inner_text("#verdict-state")
    page.wait_for_function("wanted => document.getElementById('verdict-state').textContent === wanted",
                           arg=expected, timeout=timeout)
    return page.inner_text("#verdict-state")


def test_a_freshly_observed_floor_authorises(page):
    assert state_of(page, expected="AVANZA") == "AVANZA"


def test_an_occupied_cell_on_the_route_shows_para(app, page):
    """The memorable moment: something lands on the route and the screen stops authorising."""
    site, _ = app
    cell = tuple(site.route[1])
    occupied = CellObservation(cell, time.time(), 0.95, False, "ring", site.runtime.device_id)
    site.runtime.state.cells[(site.runtime.device_id, cell)] = occupied
    assert state_of(page, expected="PARA") == "PARA"
    assert "ocupa" in page.inner_text("#verdict-reason")


def test_an_uncalibrated_phone_observes_but_never_writes_to_the_map(app):
    """A frame the site cannot place on the floor must not invent a cell."""
    site, _ = app
    frame = np.full((120, 160), 40, dtype=np.float32)
    site.observe_onboard(frame)
    frame[30:90, 40:120] = 220.0
    result = site.observe_onboard(frame)
    assert result["written"] == 0
    assert "no está calibrado" in result["reason"]
    # Aun sin escribir, sí dice qué ve al frente: es contexto, no silencio.
    assert result["clearance"]["state"] in {"CLEAR", "OBSTACLE", "UNCERTAIN"}


def test_the_screen_never_shows_a_state_the_core_did_not_decide(page):
    page.wait_for_timeout(300)
    assert state_of(page) in {"AVANZA", "CUIDADO", "PARA", "SIN CERTEZA"}


def test_every_screen_renders_without_console_errors(page):
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    for screen in ("ahora", "caminata", "sistema"):
        page.click(f".tabs button[data-goto='{screen}']")
        page.wait_for_timeout(500)
        assert page.is_visible(f".screen[data-screen='{screen}']")
    assert errors == []


def test_navigation_only_exposes_the_three_product_destinations(page):
    labels = page.locator(".tabs button").all_text_contents()
    assert labels == ["Ahora", "Caminata", "Sistema"]


def test_map_details_and_evidence_live_inside_now(page):
    page.click(".tabs button[data-goto='ahora']")
    page.click("#evidence-toggle")
    page.click(".compact-details summary")
    page.wait_for_timeout(300)
    assert page.is_visible("#evidence-panel")
    assert page.is_visible("#zones")


def test_the_walk_screen_does_not_offer_recording(page):
    page.click(".tabs button[data-goto='caminata']")
    page.wait_for_timeout(300)
    text = page.inner_text(".screen[data-screen='caminata']").lower()
    assert "grabar" not in text and "galería" not in text
    assert "no se guarda video" in text
