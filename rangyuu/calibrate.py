# calibrate.py: turns measured floor points into a homography and, crucially, into an error
# in centimetres. A calibration nobody has measured is not a calibration: every helper here
# reports how far the model lands from the tape measure, never just "it worked".

from dataclasses import dataclass
from math import hypot

from .geometry import homography_dlt, project_point


@dataclass(frozen=True)
class Correspondence:
    """One point seen in the image and measured on the floor. Metres, not pixels, on the right."""

    pixel: tuple
    floor: tuple
    label: str = ""


@dataclass(frozen=True)
class Calibration:
    """A homography plus the evidence of how wrong it is."""

    homography: list
    errors_cm: tuple
    labels: tuple

    @property
    def max_error_cm(self) -> float:
        return round(max(self.errors_cm), 1) if self.errors_cm else 0.0

    @property
    def mean_error_cm(self) -> float:
        return round(sum(self.errors_cm) / len(self.errors_cm), 1) if self.errors_cm else 0.0

    def as_dict(self) -> dict:
        return {"mean_error_cm": self.mean_error_cm, "max_error_cm": self.max_error_cm,
                "per_point_cm": {label: round(error, 1)
                                 for label, error in zip(self.labels, self.errors_cm)}}


def rectangle(width_m: float, height_m: float) -> tuple:
    """Floor coordinates of a measured rectangle, counter-clockwise from its near-left corner."""
    if width_m <= 0 or height_m <= 0:
        raise ValueError("rectangle sides must be positive")
    return ((0.0, 0.0), (width_m, 0.0), (width_m, height_m), (0.0, height_m))


def calibrate(correspondences) -> Calibration:
    """Fit the homography and measure it against the same points, in centimetres."""
    points = list(correspondences)
    if len(points) < 4:
        raise ValueError("need at least four measured correspondences")
    homography = homography_dlt([c.pixel for c in points], [c.floor for c in points])
    errors = []
    for index, point in enumerate(points):
        x, y = project_point(homography, point.pixel)
        errors.append(hypot(x - point.floor[0], y - point.floor[1]) * 100.0)
    labels = tuple(c.label or f"p{index}" for index, c in enumerate(points))
    return Calibration(homography, tuple(errors), labels)


def check_point(calibration: Calibration, pixel, expected_floor) -> float:
    """Error in centimetres for a point that was NOT used to fit — the only honest check."""
    x, y = project_point(calibration.homography, pixel)
    return round(hypot(x - expected_floor[0], y - expected_floor[1]) * 100.0, 1)
