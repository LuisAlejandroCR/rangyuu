# test_i18n_e2e.py: la interfaz en los dos idiomas, en un navegador real. Prueba que el idioma
# sale del navegador, que el control de Sistema lo anula y sobrevive a una recarga, y que traducir
# es solo presentación: el contrato y la decisión no se mueven. Se distingue de test_app_e2e.py,
# que prueba qué muestra la pantalla, no en qué idioma.

import threading
from http.server import HTTPServer

import pytest

from rangyuu.serve import build_site
from rangyuu.webapp import make_handler

playwright_api = pytest.importorskip("playwright.sync_api")

PHONE = {"width": 390, "height": 844}
DESKTOP = {"width": 1280, "height": 900}


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
        except Exception as error:
            pytest.skip(f"chromium no disponible: {error}")
        yield instance
        instance.close()


def open_app(browser, url, locale, viewport=PHONE):
    """Abre la app y espera a que el sitio haya contestado, por condición y no por reloj."""
    context = browser.new_context(viewport=viewport, locale=locale)
    page = context.new_page()
    page.goto(url, wait_until="networkidle")
    page.wait_for_function("document.querySelectorAll('#zone-chips li').length > 0", timeout=8000)
    return context, page


@pytest.mark.parametrize("locale,tab,state,gate", [
    ("es-ES", "Caminata", "AVANZA", "autoriza el paso"),
    ("en-US", "On board", "GO", "clear to proceed"),
])
def test_the_interface_follows_the_language_the_browser_asks_for(app, browser, locale, tab, state,
                                                                 gate):
    context, page = open_app(browser, app[1], locale)
    try:
        page.wait_for_function("wanted => document.getElementById('verdict-state').textContent"
                               " === wanted", arg=state, timeout=8000)
        assert page.locator(".tabs button").all_text_contents()[1] == tab
        assert page.inner_text("#verdict-gate") == gate
        assert page.get_attribute("html", "lang") == locale.split("-")[0]
    finally:
        context.close()


def test_an_unknown_language_falls_back_to_english(app, browser):
    context, page = open_app(browser, app[1], "ja-JP")
    try:
        assert page.get_attribute("html", "lang") == "en"
        assert page.locator(".tabs button").all_text_contents() == ["Now", "On board", "System"]
    finally:
        context.close()


def test_the_second_destination_is_never_named_after_walking_in_english(app, browser):
    """B4: el consumidor es cualquier vehículo autónomo o asistido, no una persona a pie."""
    context, page = open_app(browser, app[1], "en-US")
    try:
        page.click(".tabs button[data-goto='caminata']")
        page.wait_for_selector(".screen[data-screen='caminata']", state="visible")
        text = page.inner_text("body").lower()
        for word in ("walk", "walking", "pedestrian", "on foot", "step"):
            assert word not in text, f"«{word}» estrecha el producto a gente caminando"
    finally:
        context.close()


def test_the_override_wins_over_the_browser_and_survives_a_reload(app, browser):
    context, page = open_app(browser, app[1], "en-US")
    try:
        page.click(".tabs button[data-goto='sistema']")
        page.wait_for_function("document.querySelectorAll('#sources li').length > 0", timeout=8000)
        page.select_option("#language", "es")
        page.wait_for_function("document.documentElement.lang === 'es'", timeout=8000)
        assert page.locator(".tabs button").all_text_contents() == ["Ahora", "Caminata", "Sistema"]

        page.reload(wait_until="networkidle")
        page.wait_for_function("document.documentElement.lang === 'es'", timeout=8000)
        assert page.locator(".tabs button").all_text_contents() == ["Ahora", "Caminata", "Sistema"]

        # y volver a "el del navegador" devuelve el inglés sin recargar
        page.click(".tabs button[data-goto='sistema']")
        page.select_option("#language", "")
        page.wait_for_function("document.documentElement.lang === 'en'", timeout=8000)
    finally:
        context.close()


def test_changing_the_language_moves_no_decision(app, browser):
    """Traducir es presentación: el estado y la autorización del contrato no se tocan."""
    context, page = open_app(browser, app[1], "es-ES")
    try:
        page.wait_for_function(
            "document.getElementById('verdict-state').textContent !== 'SIN CERTEZA'", timeout=8000)
        before = page.evaluate("() => fetch('/api/space/now').then(r => r.json())")
        page.click(".tabs button[data-goto='sistema']")
        page.wait_for_function("document.querySelectorAll('#sources li').length > 0", timeout=8000)
        page.select_option("#language", "en")
        page.wait_for_function("document.documentElement.lang === 'en'", timeout=8000)
        after = page.evaluate("() => fetch('/api/space/now').then(r => r.json())")
        assert before["state"] == after["state"]
        assert before["authorizes"] == after["authorizes"]
        assert before["decision"] == after["decision"]
    finally:
        context.close()


def test_neither_language_overflows_the_cards_or_the_bottom_nav(app, browser):
    """El castellano es 20-30 % más largo que el inglés, y ahí es donde revienta un layout."""
    for locale in ("es-ES", "en-US"):
        for viewport in (PHONE, DESKTOP):
            context, page = open_app(browser, app[1], locale, viewport)
            try:
                for screen in ("ahora", "caminata", "sistema"):
                    page.click(f".tabs button[data-goto='{screen}']")
                    page.wait_for_selector(f".screen[data-screen='{screen}']", state="visible")
                    assert not page.evaluate(
                        "() => document.documentElement.scrollWidth > window.innerWidth"), \
                        f"scroll horizontal en {locale}/{viewport['width']}/{screen}"
                # ninguna etiqueta de la navegación se desborda de su propio botón
                assert not page.evaluate(
                    "() => [...document.querySelectorAll('.tabs button')]"
                    ".some(b => b.scrollWidth > b.clientWidth + 1)"), \
                    f"la navegación se desborda en {locale}/{viewport['width']}"
            finally:
                context.close()


def test_a_reason_with_no_translation_is_shown_as_is_rather_than_hidden(app, browser):
    context, page = open_app(browser, app[1], "en-US")
    try:
        shown = page.evaluate(
            "async () => { const m = await import('./i18n.js');"
            "  return [m.s('algo ocupa el camino'), m.s('una razón que nadie tradujo')]; }")
        assert shown == ["something is on the path", "una razón que nadie tradujo"]
    finally:
        context.close()


@pytest.mark.parametrize("locale,names", [
    ("en-US", ["entrance", "hallway", "door"]),
    ("es-ES", ["entrada", "pasillo", "puerta"]),
])
def test_the_seeded_zones_are_named_in_the_interface_language(app, browser, locale, names):
    """Los nombres de zona son dato y viajan en castellano; se traducen al mostrarlos, en los
    chips del mapa y en la lista de zonas, sin cambiar lo que guarda el servidor."""
    context, page = open_app(browser, app[1], locale)
    try:
        chips = page.locator("#zone-chips li").all_text_contents()
        listed = page.locator("#zones .label").all_text_contents()
        assert [chip.split(" · ")[0] for chip in chips] == names
        assert listed == names
        assert [zone.name for zone in app[0].zones] == ["entrada", "pasillo", "puerta"]
    finally:
        context.close()
