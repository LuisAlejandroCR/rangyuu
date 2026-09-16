# site.py: everything one site knows, assembled for the screens. Owns the runtime, the named
# zones, the calibration and a short log of decisions. It answers questions; it never decides
# anything the core did not already decide.

import time
from dataclasses import dataclass

from .calibrate import Calibration
from .onboard import CLEAR, OBSTACLE, Clearance, ClearanceFilter, ForwardClearance
from .vision import ModelUnavailable, ObjectEye
from .policy import cell_is_stale
from .runtime import LocalRuntime
from .ui import to_screen

MAX_DECISIONS = 50


@dataclass
class Zone:
    """A named area of the floor, in cells. Names are for humans, cells are for the policy."""

    name: str
    cells: tuple
    risky: bool = False

    def as_dict(self) -> dict:
        return {"name": self.name, "cells": [list(c) for c in self.cells], "risky": self.risky}


@dataclass
class Source:
    """One thing that can observe the space, and the truth about its current state."""

    key: str
    label: str
    kind: str
    active: bool = False
    last_seen: float | None = None
    note: str = ""

    def as_dict(self, now: float) -> dict:
        age = None if self.last_seen is None else round(now - self.last_seen, 1)
        return {"key": self.key, "label": self.label, "kind": self.kind,
                "active": self.active, "age_s": age, "note": self.note}


class Site:
    def __init__(self, runtime: LocalRuntime, *, calibration: Calibration | None = None,
                 error_ceiling_cm: float = 1.5, measured_error_cm: float | None = None,
                 clock=time.time):
        self.runtime = runtime
        self.calibration = calibration
        # The fit error is always ~0 and proves nothing. This is the error measured against
        # points that were NOT part of the fit, which is the number the screen must show.
        self.measured_error_cm = measured_error_cm
        self.error_ceiling_cm = float(error_ceiling_cm)
        self.clock = clock
        self.onboard_homography = None
        # Con modelo ONNX configurado, la caminata nombra lo que ve; sin él cae en la heurística
        # de texturas, que es más pobre y así lo declara. Nunca se finge tener modelo.
        try:
            self.onboard = ObjectEye()
            self.onboard_kind = "onnx"
        except (ModelUnavailable, ImportError, OSError):
            self.onboard = ForwardClearance()
            self.onboard_kind = "texturas"
        self.onboard_filter = ClearanceFilter(clock=self.clock)
        self.onboard_reading = None
        self.zones: list = []
        self.route: list = []
        self.decisions: list = []
        self.sources = {
            "ring": Source("ring", "Ring (infraestructura)", "RING_INFRASTRUCTURE"),
            "iphone": Source("iphone", "iPhone (a bordo)", "IPHONE_ONBOARD"),
        }

    # --- what the screens read --------------------------------------------

    def now(self) -> dict:
        """Screen 1. The state, the reason, the route and the cells behind both."""
        moment = self.clock()
        route = self.route or []
        report = self.runtime.can_traverse([list(c) for c in route], moment)
        screen = to_screen(report, confidence=self._path_confidence(route),
                           age_fraction=self._age_fraction(route, moment),
                           adjacent_occupied=self._adjacent_occupied(route, moment),
                           onboard=self._onboard_state(moment))
        payload = {**screen.as_dict(), "decision": report["decision"],
                   "route": [list(c) for c in route], "at": moment,
                   "cells": self._cells(moment), "evidence": report.get("evidence", {})}
        self._log(payload)
        return payload

    def map(self) -> dict:
        """Screen 3. The occupancy map plus the names humans gave it."""
        moment = self.clock()
        return {"cell_size_m": self.runtime.state.cell_size, "at": moment,
                "zones": [z.as_dict() for z in self.zones], "cells": self._cells(moment),
                "route": [list(c) for c in self.route]}

    def source_report(self) -> dict:
        """Screen 4. Limits first: what is observing, what is stale, what needs recalibrating."""
        moment = self.clock()
        self.sources["ring"].active = not self.runtime.feed_is_stale(moment)
        self.sources["ring"].last_seen = self.runtime.last_frame_at
        observed = self._cells(moment)
        known = [c for c in observed if c["state"] != "UNKNOWN"]
        return {
            "at": moment,
            "sources": [s.as_dict(moment) for s in self.sources.values()],
            "calibration": self._calibration(),
            "coverage": {"cells_known": len(known), "cells_seen": len(observed)},
            "onboard": ({**self.onboard_reading[0].as_dict(), "detector": self.onboard_kind}
                        if self.onboard_reading else {"detector": self.onboard_kind}),
            "budget_ms": self.runtime.budget.as_dict(),
        }

    def decision_log(self) -> dict:
        """Screen 6. Decisions, not clips."""
        return {"decisions": list(reversed(self.decisions))}

    # --- what the screens write -------------------------------------------

    def set_route(self, cells) -> None:
        self.route = [tuple(int(v) for v in cell) for cell in cells]

    def set_zones(self, zones) -> None:
        self.zones = [Zone(str(z["name"]), tuple(tuple(c) for c in z.get("cells", [])),
                           bool(z.get("risky", False))) for z in zones]

    def set_cell_size(self, cell_size_m: float) -> dict:
        """Rebuild the grid. Changing the cell size invalidates every observation, and this
        says so with a number instead of quietly reinterpreting old cells at a new scale."""
        size = float(cell_size_m)
        if not 0.05 <= size <= 5:
            raise ValueError("el tamaño de celda debe estar entre 0,05 y 5 m")
        cleared = len(self.runtime.state.cells)
        state = self.runtime.state
        state.cell_size = size
        state.cells.clear()
        state.events.clear()
        state.contradictions.clear()
        return {"cell_size_m": size, "cleared": cleared}

    def observe_onboard(self, gray, *, now=None, decode_ms: float = 0.0) -> dict:
        """Screen 2. A frame from the phone.

        Without its own calibration the phone cannot be placed on the floor plan: projecting it
        through the fixed camera's homography writes cells that were never observed. So an
        uncalibrated onboard source reports what it saw and writes nothing.
        """
        moment = self.clock() if now is None else now
        self.sources["iphone"].active = True
        self.sources["iphone"].last_seen = moment
        raw = self.onboard.look(gray)
        objects = getattr(self.onboard, "last_objects", None)
        # Lo que se muestra es la lectura suavizada: la cruda parpadea varias veces por segundo.
        steady = self.onboard_filter.push(raw)
        reading = raw if raw.state == steady else Clearance(steady, raw.confidence, raw.contrast,
                                                            raw.dark_fraction)
        self.onboard_reading = (reading, moment)
        self.sources["iphone"].note = {
            CLEAR: "camino despejado al frente",
            OBSTACLE: "algo al frente que no es el suelo",
        }.get(reading.state, "no puede afirmar qué hay al frente")
        if self.onboard_homography is None:
            return {"written": 0, "clearance": {**reading.as_dict(), "detector": self.onboard_kind,
                                                "objects": objects or []},
                    "reason": "el iPhone no está calibrado contra este suelo: observa, no escribe"}
        return {**self.runtime.on_frame(gray, now=moment, decode_ms=decode_ms),
                "clearance": reading.as_dict()}

    # --- internals ---------------------------------------------------------

    def _cells(self, moment: float) -> list:
        out = []
        for (device, cell), observation in self.runtime.state.cells.items():
            if device != self.runtime.device_id:
                continue
            stale = cell_is_stale(observation.observed_at, moment, self.runtime.state.max_age)
            state = "UNKNOWN" if stale else ("FREE" if observation.free else "OCCUPIED")
            out.append({"cell": list(cell), "state": state,
                        "confidence": round(observation.confidence, 3),
                        "age_s": round(moment - observation.observed_at, 1),
                        "source": observation.source})
        return sorted(out, key=lambda c: (c["cell"][1], c["cell"][0]))

    def _onboard_state(self, moment):
        """The onboard reading, only while it is fresh. Stale context is no context."""
        if self.onboard_reading is None:
            return None
        reading, at = self.onboard_reading
        return reading.state if moment - at <= self.runtime.stale_after else None

    def _observations(self, route):
        for cell in route:
            found = self.runtime.state.cells.get((self.runtime.device_id, tuple(cell)))
            if found is not None:
                yield found

    def _path_confidence(self, route):
        values = [o.confidence for o in self._observations(route)]
        return min(values) if values else None

    def _age_fraction(self, route, moment):
        ages = [(moment - o.observed_at) / self.runtime.state.max_age
                for o in self._observations(route)]
        return max(ages) if ages else None

    def _adjacent_occupied(self, route, moment) -> bool:
        route_cells = {tuple(c) for c in route}
        neighbours = {(c[0] + dx, c[1] + dy) for c in route_cells
                      for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - route_cells
        for cell in neighbours:
            found = self.runtime.state.cells.get((self.runtime.device_id, cell))
            if found is not None and not found.free and not cell_is_stale(
                    found.observed_at, moment, self.runtime.state.max_age):
                return True
        return False

    def _calibration(self) -> dict:
        if self.calibration is None:
            return {"valid": False, "reason": "sin calibrar", "error_cm": None,
                    "ceiling_cm": self.error_ceiling_cm}
        error = self.calibration.max_error_cm if self.measured_error_cm is None else self.measured_error_cm
        valid = error <= self.error_ceiling_cm
        return {"valid": valid, "error_cm": error, "ceiling_cm": self.error_ceiling_cm,
                "fit_error_cm": self.calibration.max_error_cm,
                "measured": self.measured_error_cm is not None,
                "reason": "calibración válida" if valid else "requiere recalibración"}

    def _log(self, payload) -> None:
        entry = {key: payload[key] for key in ("state", "reason", "decision", "at", "evidence")}
        if self.decisions and self.decisions[-1]["state"] == entry["state"] \
                and self.decisions[-1]["reason"] == entry["reason"]:
            return                                   # only transitions are worth logging
        self.decisions.append(entry)
        del self.decisions[:-MAX_DECISIONS]
