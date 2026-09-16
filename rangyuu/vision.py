# vision.py: the onboard lane with a real object detector. Runs an ONNX model locally — no frame
# leaves the machine — and only reports objects standing in the walked corridor. It replaces the
# texture heuristic of onboard.py, which was measured at 22% precision and could only warn.

import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from . import config
from .onboard import CLEAR, OBSTACLE, UNCERTAIN, Clearance

# COCO ids that can block a person walking. Anything else on the floor is not this lane's problem.
BLOCKING = {
    1: "persona", 2: "bicicleta", 3: "auto", 4: "moto", 6: "bus", 8: "camión",
    17: "gato", 18: "perro", 21: "vaca", 62: "silla", 63: "sofá", 64: "planta", 67: "mesa",
    72: "televisor", 73: "portátil", 84: "libro", 86: "florero",
}
CORRIDOR = (0.15, 0.85)      # the width of the path ahead, as a fraction of the frame
MIN_SCORE = 0.45
NEAR_BOTTOM = 0.55           # a box reaching this far down the frame is close enough to matter
MODEL_ENV = "RANGYUU_ONNX_MODEL"


class ModelUnavailable(RuntimeError):
    """Raised when no model is configured. The caller must degrade, never pretend."""


@dataclass(frozen=True)
class Sighting:
    """One detected object, with what it is and how much of the corridor it takes."""

    label: str
    score: float
    box: tuple                # (top, left, bottom, right) in fractions of the frame
    in_corridor: bool
    near: bool

    def as_dict(self) -> dict:
        return {"label": self.label, "score": round(self.score, 2),
                "box": [round(v, 3) for v in self.box],
                "in_corridor": self.in_corridor, "near": self.near}


class ObjectEye:
    """Local ONNX object detection over walking frames.

    The model file is not versioned: it is 29 MB and belongs to whoever runs the site. Point
    RANGYUU_ONNX_MODEL at it. Without a model this class raises, so the caller degrades openly
    instead of silently falling back to something weaker.
    """

    def __init__(self, model_path=None, *, min_score: float = MIN_SCORE, providers=None):
        path = str(model_path or config.get(MODEL_ENV))
        if not path or not Path(path).is_file():
            raise ModelUnavailable(f"no hay modelo ONNX: definí {MODEL_ENV} con la ruta del archivo")
        import onnxruntime as ort

        self.path = path
        self.min_score = float(min_score)
        self.session = ort.InferenceSession(path, providers=providers or ["CPUExecutionProvider"])
        self.input_name = self.session.get_inputs()[0].name
        self.last_ms = 0.0
        self.last_objects = []

    # --- inference --------------------------------------------------------

    def sightings(self, rgb) -> list:
        """Every blocking object the model sees, with its place in the frame."""
        image = np.asarray(rgb, dtype=np.uint8)
        if image.ndim != 3 or image.shape[2] != 3:
            raise ValueError("se necesita un frame RGB de alto x ancho x 3")
        started = time.perf_counter()
        boxes, classes, scores, _ = self.session.run(None, {self.input_name: image[None]})
        self.last_ms = (time.perf_counter() - started) * 1000.0

        found = []
        for box, class_id, score in zip(boxes[0], classes[0], scores[0]):
            label = BLOCKING.get(int(class_id))
            if label is None or float(score) < self.min_score:
                continue
            top, left, bottom, right = (float(v) for v in box)
            centre = (left + right) / 2
            found.append(Sighting(label, float(score), (top, left, bottom, right),
                                  in_corridor=CORRIDOR[0] <= centre <= CORRIDOR[1],
                                  near=bottom >= NEAR_BOTTOM))
        return found

    def look(self, rgb) -> Clearance:
        """The same verdict shape the texture heuristic returns, so the lane is interchangeable."""
        found = self.sightings(rgb)
        self.last_objects = [s.as_dict() for s in found]
        blocking = [s for s in found if s.in_corridor]
        if not blocking:
            return Clearance(CLEAR, 0.9, 0.0, 0.0)
        strongest = max(blocking, key=lambda s: s.score)
        # Something in the corridor and close is an obstacle; far away it is a warning, not a stop.
        state = OBSTACLE if strongest.near else UNCERTAIN
        return Clearance(state, strongest.score, 0.0, 0.0)

    def describe(self, rgb) -> dict:
        """What the walking screen shows: the verdict plus what was actually recognised."""
        verdict = self.look(rgb)
        return {**verdict.as_dict(), "inference_ms": round(self.last_ms, 1),
                "objects": list(self.last_objects)}
