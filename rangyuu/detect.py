# detect.py: local motion detection over decoded frames. Deliberately dependency-free and
# offline by construction: it opens no socket, so no frame can leave the site to be inferred.
# A heavier model can replace it behind the same detect() signature.

import time
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Detection:
    """One blob found on the frame, in pixels, with the confidence that produced it."""

    bbox: tuple           # (x, y, width, height)
    confidence: float
    pixels: int


@dataclass(frozen=True)
class DetectionBatch:
    """What one frame produced, plus how long the inference itself took."""

    detections: tuple
    inference_ms: float
    frame_index: int


class MotionDetector:
    """Running-average background subtraction. Cheap, local, and good enough for occupancy."""

    def __init__(self, *, threshold: float = 18.0, min_pixels: int = 120, decay: float = 0.08,
                 downscale: int = 4):
        if not 0 < decay <= 1 or threshold <= 0 or downscale < 1:
            raise ValueError("invalid detector settings")
        self.threshold = float(threshold)
        self.min_pixels = int(min_pixels)
        self.decay = float(decay)
        self.downscale = int(downscale)
        self._background = None
        self._frames = 0

    def detect(self, gray: np.ndarray) -> DetectionBatch:
        """Run inference on one grayscale frame. Returns boxes in full-frame pixel coordinates."""
        started = time.perf_counter()
        small = np.asarray(gray, dtype=np.float32)[:: self.downscale, :: self.downscale]
        if self._background is None:
            self._background = small.copy()
            return DetectionBatch((), (time.perf_counter() - started) * 1000.0, self._bump())
        difference = np.abs(small - self._background)
        self._background += self.decay * (small - self._background)
        mask = difference > self.threshold
        detections = tuple(self._boxes(mask, difference))
        return DetectionBatch(detections, (time.perf_counter() - started) * 1000.0, self._bump())

    def _bump(self) -> int:
        self._frames += 1
        return self._frames

    def _boxes(self, mask, difference):
        """One box per connected column band. Rough on purpose: the grid is the precise part."""
        columns = mask.any(axis=0)
        start = None
        for index, active in enumerate(list(columns) + [False]):
            if active and start is None:
                start = index
            elif not active and start is not None:
                band = mask[:, start:index]
                count = int(band.sum())
                if count >= self.min_pixels // (self.downscale ** 2):
                    rows = np.nonzero(band.any(axis=1))[0]
                    y0, y1 = int(rows[0]), int(rows[-1])
                    confidence = float(min(1.0, difference[:, start:index].max() / 255.0 * 3))
                    yield Detection(
                        bbox=(start * self.downscale, y0 * self.downscale,
                              (index - start) * self.downscale, (y1 - y0 + 1) * self.downscale),
                        confidence=round(confidence, 3), pixels=count * self.downscale ** 2)
                start = None
