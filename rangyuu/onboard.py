# onboard.py: the walking camera. It has no calibration against this floor, so it never claims
# metres or cells: it only answers whether the strip of floor straight ahead still looks like the
# floor. Its verdict may degrade a decision, never authorise one on its own.

import time
from dataclasses import dataclass

import numpy as np

CLEAR = "CLEAR"
OBSTACLE = "OBSTACLE"
UNCERTAIN = "UNCERTAIN"

# Empeorar es inmediato; mejorar exige acuerdo y tiempo. Este orden es esa asimetría.
SEVERITY = {CLEAR: 0, UNCERTAIN: 1, OBSTACLE: 2}

NEAR_BAND = (0.75, 1.00)     # bottom of the frame: the floor under the walker's feet
AHEAD_BAND = (0.45, 0.72)    # a few steps ahead, where an obstacle would appear first
CENTRE = (0.28, 0.72)        # the width of the path being walked


@dataclass(frozen=True)
class Clearance:
    """What the onboard camera can honestly say about the way ahead."""

    state: str
    confidence: float
    contrast: float
    dark_fraction: float

    @property
    def degrades(self) -> bool:
        """True when this reading must pull a decision down, never up."""
        return self.state != CLEAR

    def as_dict(self) -> dict:
        return {"state": self.state, "confidence": round(self.confidence, 3),
                "contrast": round(self.contrast, 2), "dark_fraction": round(self.dark_fraction, 3)}


class ForwardClearance:
    """Compares the strip ahead with the floor under the feet, which is known to be floor.

    Anything that does not look like that floor — a person, a step, a box, a wall — raises the
    difference. No depth, no distance: the answer is only clear, obstacle or uncertain.
    """

    def __init__(self, *, obstacle_contrast: float = 22.0, uncertain_contrast: float = 12.0,
                 dark_limit: float = 0.35, lit_floor: float = 60.0):
        if not 0 < uncertain_contrast < obstacle_contrast:
            raise ValueError("los umbrales deben crecer de incierto a obstáculo")
        self.obstacle_contrast = float(obstacle_contrast)
        self.uncertain_contrast = float(uncertain_contrast)
        self.dark_limit = float(dark_limit)
        self.lit_floor = float(lit_floor)

    def look(self, gray) -> Clearance:
        frame = np.asarray(gray, dtype=np.float32)
        if frame.ndim != 2 or min(frame.shape) < 16:
            raise ValueError("se necesita un frame en escala de grises de al menos 16x16")
        near = _band(frame, NEAR_BAND)
        ahead = _band(frame, AHEAD_BAND)
        if near.size == 0 or ahead.size == 0:
            return Clearance(UNCERTAIN, 0.0, 0.0, 1.0)

        reference = float(np.median(near))
        contrast = float(np.median(np.abs(ahead - reference)))
        dark = float(np.mean(ahead < max(18.0, reference * 0.45)))

        # Too dark to judge is not the same as blocked, and neither one is free. The difference
        # is what is under the feet: with a lit floor underneath, a dark strip ahead is an object
        # standing in the way, not darkness. Only when both are dark is the reading useless.
        if dark > self.dark_limit:
            underfoot_lit = reference >= self.lit_floor
            return Clearance(OBSTACLE if underfoot_lit else UNCERTAIN,
                             0.6 if underfoot_lit else 0.25, contrast, dark)
        if contrast >= self.obstacle_contrast:
            return Clearance(OBSTACLE, min(1.0, contrast / (self.obstacle_contrast * 2)), contrast, dark)
        if contrast >= self.uncertain_contrast:
            return Clearance(UNCERTAIN, 0.4, contrast, dark)
        return Clearance(CLEAR, min(1.0, 1.0 - contrast / self.obstacle_contrast), contrast, dark)


def _band(frame, band):
    height, width = frame.shape
    top, bottom = int(height * band[0]), int(height * band[1])
    left, right = int(width * CENTRE[0]), int(width * CENTRE[1])
    return frame[top:bottom, left:right]


class ClearanceFilter:
    """Smooths the readings in time, asymmetrically: quick to stop, slow to clear again.

    A raw reading flips several times a second while walking, which is useless to a person and
    unbearable as haptics. So a degrade lands immediately, and returning to CLEAR needs both a
    run of agreeing readings and a minimum dwell, so the walker is not waved forward too early.
    """

    def __init__(self, *, agree: int = 4, dwell_s: float = 1.2, clock=None):
        if agree < 1 or dwell_s < 0:
            raise ValueError("agree debe ser al menos 1 y dwell_s no puede ser negativo")
        self.agree = int(agree)
        self.dwell_s = float(dwell_s)
        self.clock = clock or time.monotonic
        self.state = UNCERTAIN
        self.since = self.clock()
        self._run = 0
        self._candidate = UNCERTAIN

    def push(self, reading: Clearance) -> str:
        now = self.clock()
        incoming = reading.state

        if SEVERITY[incoming] > SEVERITY[self.state]:         # empeorar es inmediato
            self.state, self.since, self._run, self._candidate = incoming, now, 0, incoming
            return self.state

        if incoming == self._candidate:
            self._run += 1
        else:
            self._candidate, self._run = incoming, 1

        held_long_enough = (now - self.since) >= self.dwell_s
        if incoming != self.state and self._run >= self.agree and held_long_enough:
            self.state, self.since, self._run = incoming, now, 0
        return self.state
