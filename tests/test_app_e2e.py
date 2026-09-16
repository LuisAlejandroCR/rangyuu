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
def browser():
    with playwright_api.sync_playwright() as p:
        try:
            instance = p.chromium.launch()
        except Exception as error:                      # no browser installed in this environment
            pytest.skip(f"chromium no disponible: {error}")
        yield instance
        instance.close()


PHONE = {"width": 390, "height": 844}


@pytest.fixture(scope="module")
def page(app, browser):
    # El idioma va declarado: la interfaz sigue al navegador, así que sin `locale` estas pruebas
    # dependerían del idioma de la máquina que las corre. Acá se fija el castellano a propósito.
    page = browser.new_page(viewport=PHONE, locale="es-ES")
    page.goto(app[1], wait_until="networkidle")
    yield page
    page.close()


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


def test_losing_the_link_to_the_site_withdraws_the_authorisation(app, page):
    """Perder el enlace es quedarse sin evidencia, y sin evidencia no se autoriza.

    Antes la pantalla dejaba el último estado en grande —un AVANZA verde— y solo cambiaba la
    razón en letra chica, así que seguía autorizando sobre un dato que ya no tenía.
    """
    page.click(".tabs button[data-goto='ahora']")
    page.wait_for_function(
        "document.getElementById('verdict-state').textContent !== 'SIN CERTEZA'", timeout=8000)
    page.evaluate("() => { window.__fetch = window.fetch;"
                  "        window.fetch = () => Promise.reject(new Error('down')); return true; }")
    try:
        page.wait_for_function(
            "document.getElementById('verdict-state').textContent === 'SIN CERTEZA'", timeout=8000)
        assert "sin enlace" in page.inner_text("#verdict-reason")
        assert page.inner_text("#verdict-gate") == "no autoriza el paso"
    finally:
        page.evaluate("() => { window.fetch = window.__fetch; return true; }")
    page.wait_for_function(
        "document.getElementById('verdict-state').textContent !== 'SIN CERTEZA'", timeout=8000)


AUTHORISING = {"AVANZA", "CUIDADO"}


def test_the_screen_says_whether_it_authorises_rather_than_only_colouring_it(page):
    """El bit que importa sale del contrato (`authorizes`), no de leerle el color al estado."""
    state = state_of(page)
    gate = page.inner_text("#verdict-gate")
    assert gate == ("autoriza el paso" if state in AUTHORISING else "no autoriza el paso")


def test_the_app_loads_without_a_single_console_error(app, browser):
    """La consola se escucha desde antes de `goto`: el error de arranque no se veía de otro modo.

    `navigator.vibrate()` antes del primer gesto lo descarta el navegador y lo anota como error.
    """
    fresh = browser.new_page(viewport=PHONE, locale="es-ES")
    errors = []
    fresh.on("pageerror", lambda e: errors.append(str(e)))
    fresh.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    try:
        fresh.goto(app[1], wait_until="networkidle")
        fresh.wait_for_function("document.querySelectorAll('#zone-chips li').length > 0",
                                timeout=8000)
        assert errors == []
    finally:
        fresh.close()


def test_zone_names_are_legible_html_instead_of_svg_text_that_scales_with_the_grid(page):
    """Dentro del SVG el texto se medía en unidades del viewBox y se desbordaba de la tarjeta."""
    page.click(".tabs button[data-goto='ahora']")
    page.wait_for_function("document.querySelectorAll('#zone-chips li').length > 0", timeout=8000)
    assert page.locator("#map-now text.zone-label").count() == 0
    overflow = page.evaluate(
        "() => {const c = document.querySelector('.map-card').getBoundingClientRect();"
        "return [...document.querySelectorAll('#zone-chips li')]"
        ".some(e => e.getBoundingClientRect().right > c.right + 1);}")
    assert not overflow


def test_the_walk_screen_does_not_offer_recording(page):
    page.click(".tabs button[data-goto='caminata']")
    page.wait_for_timeout(300)
    text = page.inner_text(".screen[data-screen='caminata']").lower()
    assert "grabar" not in text and "galería" not in text
    assert "no se guarda video" in text
