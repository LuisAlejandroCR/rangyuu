# serve.py: starts the app with a site anyone can run — no Ring credentials, no hardware.
# It seeds the floor from the measured calibration fixture and lets the screens drive the rest.
# Run: python -m rangyuu.serve  (then open http://localhost:8080)

import json
import sys
import threading
import time
from pathlib import Path

from .calibrate import Correspondence, calibrate
from .runtime import LocalRuntime
from .site import Site
from .webapp import serve

FIXTURE = Path(__file__).resolve().parent.parent / "fixtures" / "home" / "calibration_points.json"
ROUTE = [(2, 0), (2, 1), (2, 2), (2, 3)]
FLOOR = [(x, y) for x in range(1, 5) for y in range(0, 5)]
CELL_SIZE = 0.3
# Measured 2026-09-15 against tile joints that were not part of the fit: 0.9 cm over 61 cm.
MEASURED_ERROR_CM = 0.9
MAX_AGE = 20.0
REFRESH = 5.0


def measured_calibration():
    """The calibration measured on 2026-09-15, or None if the fixture is missing."""
    if not FIXTURE.is_file():
        return None
    points = json.loads(FIXTURE.read_text(encoding="utf-8"))["marks"]["points"]
    return calibrate([Correspondence(tuple(p["pixel"]), tuple(p["floor_m"]), p["label"])
                      for p in points])


def build_site() -> Site:
    calibration = measured_calibration()
    homography = calibration.homography if calibration else [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    runtime = LocalRuntime("ring-front-01", homography, cell_size=CELL_SIZE, max_age=MAX_AGE,
                           stale_after=MAX_AGE)
    site = Site(runtime, calibration=calibration,
                measured_error_cm=MEASURED_ERROR_CM if calibration else None)
    site.set_route(ROUTE)
    site.set_zones([
        {"name": "entrada", "cells": [[1, 0], [2, 0], [3, 0]]},
        {"name": "pasillo", "cells": [[2, 1], [2, 2], [2, 3]]},
        {"name": "puerta", "cells": [[2, 4], [3, 4]], "risky": True},
    ])
    seeded = time.time()
    site.runtime.mark_free(FLOOR, now=seeded)
    # The seeded floor counts as observed, otherwise the first seconds report a stale feed
    # for a site that was just calibrated. A real frame overwrites this by timestamp.
    site.runtime.last_frame_at = seeded
    return site


def keep_floor_observed(site: Site) -> None:
    """A stand-in for the camera while no feed is attached: re-observes the floor as free.

    It exists so the demo starts in a legible state. It never touches a cell an event wrote:
    the moment a real observation arrives, that observation wins by timestamp.
    """
    while True:
        time.sleep(REFRESH)
        now = time.time()
        site.runtime.last_frame_at = now
        for cell in FLOOR:
            key = (site.runtime.device_id, tuple(cell))
            current = site.runtime.state.cells.get(key)
            if current is None or current.free:
                site.runtime.mark_free([cell], now=now)


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    port = int(argv[0]) if argv else 8080
    site = build_site()
    threading.Thread(target=keep_floor_observed, args=(site,), daemon=True).start()
    serve(site, port=port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
