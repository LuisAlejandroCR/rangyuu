# runtime.py: the critical loop, in the site. Frame -> local inference -> spatial state ->
# decision, with a budget measured per stage and a watchdog that turns silence into the safe
# action. Nothing here waits on the network: if the feed dies, the decision degrades by itself.

import time
from dataclasses import dataclass, field

from .detect import MotionDetector
from .spatial import SpatialState

FREE_KIND = "path_clear"
OCCUPIED_KIND = "person"


@dataclass
class StageBudget:
    """Milliseconds per stage, measured. `count` is how many frames fed the numbers."""

    decode_ms: float = 0.0
    inference_ms: float = 0.0
    decision_ms: float = 0.0
    count: int = 0

    def add(self, decode_ms, inference_ms, decision_ms) -> None:
        self.decode_ms += decode_ms
        self.inference_ms += inference_ms
        self.decision_ms += decision_ms
        self.count += 1

    def as_dict(self) -> dict:
        if not self.count:
            return {"frames": 0}
        return {"frames": self.count,
                "decode_ms": round(self.decode_ms / self.count, 2),
                "inference_ms": round(self.inference_ms / self.count, 2),
                "decision_ms": round(self.decision_ms / self.count, 2),
                "total_ms": round((self.decode_ms + self.inference_ms + self.decision_ms) / self.count, 2)}


class LocalRuntime:
    """Owns the spatial state and the detector. One instance per site, not per camera."""

    def __init__(self, device_id: str, homography, *, max_age: float = 5.0, cell_size: float = 0.25,
                 detector=None, stale_after: float = 2.0):
        self.device_id = device_id
        self.state = SpatialState(max_age=max_age, cell_size=cell_size)
        self.state.calibrate(device_id, homography)
        self.detector = detector or MotionDetector()
        self.stale_after = float(stale_after)
        self.budget = StageBudget()
        self.last_frame_at: float | None = None
        self._events = 0

    # --- the loop ---------------------------------------------------------

    def on_frame(self, gray, now: float, *, decode_ms: float = 0.0) -> dict:
        """Feed one decoded frame. Returns what was written, never a decision: that is asked for."""
        batch = self.detector.detect(gray)
        started = time.perf_counter()
        written = 0
        for detection in batch.detections:
            self._events += 1
            self.state.ingest({"event_id": f"{self.device_id}-{self._events}",
                               "device_id": self.device_id, "timestamp": now,
                               "confidence": detection.confidence, "bounding_box": list(detection.bbox),
                               "kind": OCCUPIED_KIND, "source": "ring"})
            written += 1
        decision_ms = (time.perf_counter() - started) * 1000.0
        self.budget.add(decode_ms, batch.inference_ms, decision_ms)
        self.last_frame_at = now
        return {"detections": len(batch.detections), "written": written,
                "inference_ms": round(batch.inference_ms, 2)}

    def mark_free(self, cells, now: float, *, confidence: float = 0.9) -> None:
        """Declare cells observed free. Only a positive observation may ever do this."""
        for cell in cells:
            self._events += 1
            self.state.cells[(self.device_id, tuple(cell))] = _free(self.device_id, cell, now, confidence)

    # --- the contract -----------------------------------------------------

    def can_traverse(self, trajectory, now: float) -> dict:
        """The rover asks here. A feed gone silent is coverage lost, never a free path."""
        report = self.state.evaluate_trajectory(self.device_id, now, trajectory)
        if self.feed_is_stale(now):
            report = dict(report)
            report["decision"] = "UNKNOWN" if report["decision"] == "PROCEED" else report["decision"]
            report["action"] = "WAIT"
            report["reason"] = "feed stale: no frame within the declared window"
        report["authorizes"] = report["decision"] == "PROCEED"
        return report

    def feed_is_stale(self, now: float) -> bool:
        return self.last_frame_at is None or (now - self.last_frame_at) > self.stale_after


def _free(device_id, cell, now, confidence):
    from .spatial import CellObservation

    return CellObservation(tuple(cell), float(now), float(confidence), True, "ring", device_id)
