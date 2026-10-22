# test_haptics_e2e.py: el aviso háptico en un navegador real. Se instrumenta navigator.vibrate
# antes de cargar la página, así se comprueba el patrón que sale por cada estado sin depender
# de que el dispositivo vibre de verdad.

import threading
import time
from http.server import HTTPServer

import pytest

from rangyuu.serve import build_site
from rangyuu.spatial import CellObservation
from rangyuu.webapp import make_handler

playwright_api = pytest.importorskip("playwright.sync_api")

STUB = """
window.__vibrations = [];
navigator.vibrate = (pattern) => { window.__vibrations.push(pattern); return true; };
window.__clips = [];
window.Audio = function (src) {
  this.src = src;
  this.play = () => { window.__clips.push(src); return Promise.resolve(); };
  this.pause = () => {};
};
"""


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
        except Exception as error:
            pytest.skip(f"chromium no disponible: {error}")
        # Idioma declarado: la interfaz sigue al navegador y la voz habla en el idioma activo.
        page = browser.new_page(viewport={"width": 390, "height": 844}, locale="es-ES")
        page.add_init_script(STUB)
        page.goto(app[1], wait_until="networkidle")
        # El navegador no deja vibrar ni sonar hasta que hay un gesto del usuario, así que la
        # prueba hace el gesto en vez de fingirlo. Después espera a la primera vibración por
        # condición, no por reloj: con la máquina cargada un `wait_for_timeout` da intermitencias.
        page.click(".tabs button[data-goto='ahora']")
        page.wait_for_function("window.__vibrations.length > 0", timeout=8000)
        yield page
        browser.close()


def vibrations(page):
    return page.evaluate("window.__vibrations")


def test_the_first_state_vibrates_once(page):
    page.wait_for_function("window.__vibrations.length > 0", timeout=8000)
    assert vibrations(page), "un estado nuevo tiene que avisar"
    assert vibrations(page)[0] == [35]              # AVANZA: un toque corto


def test_the_same_state_does_not_keep_buzzing(page):
    before = len(vibrations(page))
    page.wait_for_timeout(2500)                     # varios refrescos con el mismo estado
    assert len(vibrations(page)) == before


def test_para_has_its_own_stronger_pattern(app, page):
    site, _ = app
    cell = tuple(site.route[1])
    site.runtime.state.cells[(site.runtime.device_id, cell)] = CellObservation(
        cell, time.time(), 0.95, False, "ring", site.runtime.device_id)
    page.wait_for_function("document.getElementById('verdict-state').textContent === 'PARA'",
                           timeout=8000)
    page.wait_for_function("window.__vibrations.at(-1)?.join(',') === '140,80,140'", timeout=8000)
    assert vibrations(page)[-1] == [140, 80, 140]


def test_the_voice_is_the_bundled_elevenlabs_clip_for_the_state(page):
    """Same clips as the mobile app: one per state, in the active language (es in this page)."""
    page.wait_for_function("window.__clips.some(c => c.endsWith('/es/hold.mp3'))", timeout=8000)
    clips = page.evaluate("window.__clips")
    assert any(c.endswith("/voices/lumina/es/proceed.mp3") for c in clips)
    assert clips[-1].endswith("/voices/lumina/es/hold.mp3")


def test_losing_the_link_says_so_with_its_own_clip(page):
    """Shot 5A of the demo: the server stops and the voice says the link was lost, not just 'uncertain'."""
    page.evaluate("() => { window.__fetch = window.fetch;"
                  "        window.fetch = () => Promise.reject(new Error('down')); return true; }")
    try:
        page.wait_for_function("window.__clips.at(-1)?.endsWith('/es/linkLost.mp3')", timeout=8000)
    finally:
        page.evaluate("() => { window.fetch = window.__fetch; return true; }")


def test_a_queued_clip_is_replaced_by_the_latest_state_before_the_first_gesture(app, page):
    """Loads on a state (GO when the floor is clear), loses the link before anyone touches the
    screen, then gets the gesture: the voice must say linkLost, never the old state's clip."""
    cue = {"AVANZA": "proceed", "CUIDADO": "caution", "PARA": "hold"}
    fresh = page.context.browser.new_page(viewport={"width": 390, "height": 844}, locale="es-ES")
    try:
        fresh.add_init_script(STUB)
        fresh.goto(app[1], wait_until="networkidle")
        fresh.wait_for_function(
            "document.getElementById('verdict-state').textContent !== 'SIN CERTEZA'", timeout=8000)
        first = fresh.inner_text("#verdict-state")
        fresh.evaluate("() => { window.fetch = () => Promise.reject(new Error('down')); return true; }")
        fresh.wait_for_function(
            "document.getElementById('verdict-state').textContent === 'SIN CERTEZA'", timeout=8000)
        assert fresh.evaluate("window.__clips") == []      # nothing can sound before the gesture
        fresh.click(".tabs button[data-goto='ahora']")
        fresh.wait_for_function("window.__clips.length > 0", timeout=8000)
        clips = fresh.evaluate("window.__clips")
        assert clips[0].endswith("/es/linkLost.mp3")
        assert not any(c.endswith(f"/{cue[first]}.mp3") for c in clips)
    finally:
        fresh.close()


def test_the_sources_screen_declares_which_channels_exist(page):
    page.click(".tabs button[data-goto='sistema']")
    page.wait_for_timeout(800)
    panel = page.inner_text("#haptics")
    assert "vibración" in panel and "tono" in panel and "voz" in panel


def test_the_test_button_repeats_the_current_state_on_demand(page):
    page.click(".tabs button[data-goto='sistema']")
    page.wait_for_timeout(600)
    before = len(vibrations(page))
    page.click("#haptics-toggle")
    page.wait_for_function("n => window.__vibrations.length > n", arg=before, timeout=8000)
    assert len(vibrations(page)) == before + 1
