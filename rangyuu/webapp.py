# webapp.py: the HTTP boundary the screens talk to, plus the static files themselves.
# Read endpoints answer what the site knows; write endpoints only set the route, the zones
# and the calibration. Nothing here decides: it asks the core and passes the answer through.

import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .calibrate import Correspondence, calibrate

WEB_ROOT = Path(__file__).resolve().parent.parent / "web"
# The ElevenLabs clips the mobile app bundles; served at /voices/ so the web app speaks with them.
VOICES_ROOT = Path(__file__).resolve().parent.parent / "mobile" / "assets" / "voices"
MAX_BODY = 262_144
CACHE = "no-store"


def make_handler(site, web_root: Path = WEB_ROOT):
    class Handler(BaseHTTPRequestHandler):
        # --- plumbing -----------------------------------------------------

        def _send(self, status: int, payload, content_type="application/json; charset=utf-8"):
            body = payload if isinstance(payload, bytes) else json.dumps(
                payload, separators=(",", ":"), ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", CACHE)
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        def _body(self):
            try:
                length = int(self.headers.get("Content-Length", "-1"))
            except ValueError:
                self._send(400, {"error": "invalid content length"})
                return None
            if length < 0:
                self._send(411, {"error": "content length required"})
                return None
            if length > MAX_BODY:
                self._send(413, {"error": "payload too large"})
                return None
            raw = self.rfile.read(length)
            if len(raw) != length:
                self._send(400, {"error": "truncated body"})
                return None
            try:
                value = json.loads(raw or b"{}")
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._send(400, {"error": "invalid json"})
                return None
            if not isinstance(value, dict):
                self._send(400, {"error": "json object required"})
                return None
            return value

        # --- reads --------------------------------------------------------

        def do_GET(self):
            path = self.path.split("?", 1)[0]
            routes = {
                "/api/space/now": site.now,
                "/api/space/map": site.map,
                "/api/sources": site.source_report,
                "/api/decisions": site.decision_log,
                "/api/health": lambda: {"status": "ok"},
            }
            if path in routes:
                self._send(200, routes[path]())
                return
            self._static(path)

        do_HEAD = do_GET

        def _static(self, path: str):
            root = web_root
            if path.startswith("/voices/"):
                root, path = VOICES_ROOT, path[len("/voices"):]
            relative = "index.html" if path in ("/", "") else path.lstrip("/")
            target = (root / relative).resolve()
            if root.resolve() not in target.parents or not target.is_file():
                self._send(404, {"error": "not found"})
                return
            kind = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
            charset = "; charset=utf-8" if kind.startswith("text/") or kind.endswith("javascript") else ""
            self._send(200, target.read_bytes(), kind + charset)

        # --- writes -------------------------------------------------------

        def do_POST(self):
            path = self.path.split("?", 1)[0]
            value = self._body()
            if value is None:
                return
            try:
                if path == "/api/space/route":
                    site.set_route(value.get("cells", []))
                    self._send(200, site.now())
                elif path == "/api/space/zones":
                    site.set_zones(value.get("zones", []))
                    self._send(200, site.map())
                elif path == "/api/space/calibrate":
                    self._send(200, _calibrate(site, value))
                elif path == "/api/space/config":
                    self._send(200, site.set_cell_size(value.get("cell_size_m")))
                elif path == "/api/space/observe":
                    self._send(200, _observe(site, value))
                else:
                    self._send(404, {"error": "not found"})
            except (KeyError, TypeError, ValueError) as error:
                self._send(422, {"error": str(error)})

        def log_message(self, *_args):
            return

    return Handler


def _calibrate(site, value) -> dict:
    """Fit from four measured points and report the error before anything is stored."""
    points = value.get("points") or []
    if len(points) < 4:
        raise ValueError("se necesitan cuatro puntos medidos")
    calibration = calibrate([Correspondence(tuple(p["pixel"]), tuple(p["floor_m"]),
                                            str(p.get("label", ""))) for p in points])
    accepted = calibration.max_error_cm <= site.error_ceiling_cm
    if accepted:
        site.calibration = calibration
        # The measured error belonged to the previous matrix. Carrying it over would hand a
        # new calibration a proof it never earned, so the site goes back to unverified and
        # stops authorising until someone measures this matrix against a known point.
        site.measured_error_cm = None
    return {"accepted": accepted, "ceiling_cm": site.error_ceiling_cm,
            "measured": site.measured_error_cm is not None,
            "authorizes": site.calibration_is_verified(), **calibration.as_dict()}


def _observe(site, value) -> dict:
    """A downscaled grayscale frame from the phone. It never leaves this machine."""
    import numpy as np

    width, height = int(value.get("width", 0)), int(value.get("height", 0))
    gray = value.get("gray")
    if width <= 0 or height <= 0 or not isinstance(gray, list):
        raise ValueError("se necesita width, height y gray")
    if width * height != len(gray) or len(gray) > 65_536:
        raise ValueError("el tamaño del frame no coincide con width x height")
    frame = np.asarray(gray, dtype=np.float32).reshape(height, width)
    result = site.observe_onboard(frame)
    return {**result, "now": site.now()}


def make_server(site, host="0.0.0.0", port=8080):
    # Threaded: a browser's idle preconnect socket would otherwise block every other request.
    server = ThreadingHTTPServer((host, port), make_handler(site))
    server.daemon_threads = True
    return server


def serve(site, host="0.0.0.0", port=8080):  # pragma: no cover - the blocking entry point
    server = make_server(site, host, port)
    print(f"rangyuu en http://localhost:{port}")
    server.serve_forever()
