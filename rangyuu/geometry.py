"""Planar calibration utilities based on normalized homogeneous DLT."""

from __future__ import annotations

from math import hypot, isfinite
from typing import Sequence

import numpy as np


Point = tuple[float, float]
Matrix3 = list[list[float]]


def _as_points(points: Sequence[Sequence[float]], name: str) -> list[Point]:
    """Convert point pairs to finite floats and reject malformed inputs."""
    result: list[Point] = []
    for point in points:
        if len(point) != 2:
            raise ValueError(f"{name} points must be pairs")
        x, y = float(point[0]), float(point[1])
        if not (isfinite(x) and isfinite(y)):
            raise ValueError(f"{name} points must be finite")
        result.append((x, y))
    return result


def _normalize(points: Sequence[Point]) -> tuple[list[Point], Matrix3]:
    """Apply Hartley similarity normalization and return its transform."""
    cx = sum(x for x, _ in points) / len(points)
    cy = sum(y for _, y in points) / len(points)
    mean_distance = sum(hypot(x - cx, y - cy) for x, y in points) / len(points)
    if mean_distance <= 1e-15:
        raise ValueError("degenerate correspondences")
    scale = 2.0**0.5 / mean_distance
    transform: Matrix3 = [
        [scale, 0.0, -scale * cx],
        [0.0, scale, -scale * cy],
        [0.0, 0.0, 1.0],
    ]
    normalized = [((x - cx) * scale, (y - cy) * scale) for x, y in points]
    return normalized, transform


def _homogeneous_scale(matrix: np.ndarray) -> Matrix3:
    """Choose a stable, deterministic scale without assuming h33 is nonzero."""
    norm = float(np.linalg.norm(matrix))
    if not isfinite(norm) or norm <= np.finfo(float).eps:
        raise ValueError("degenerate homography")
    scaled = matrix / norm
    # The sign of a homogeneous solution is arbitrary. Stabilize it for callers.
    first = next((float(value) for value in scaled.flat if abs(float(value)) > 1e-14), 1.0)
    if first < 0:
        scaled = -scaled
    return [[float(value) for value in row] for row in scaled]


def homography_dlt(src: Sequence[Sequence[float]], dst: Sequence[Sequence[float]]) -> Matrix3:
    """Estimate a 3x3 projective transform from matching planar points.

    The solution is the right null vector of the homogeneous DLT matrix, found by
    SVD after Hartley normalization. It therefore also supports valid transforms
    whose bottom-right coefficient ``h33`` is zero.
    """
    source = _as_points(src, "source")
    target = _as_points(dst, "destination")
    if len(source) < 4 or len(source) != len(target):
        raise ValueError("need at least four matching points")

    normalized_source, source_transform = _normalize(source)
    normalized_target, target_transform = _normalize(target)
    rows: list[list[float]] = []
    for (x, y), (u, v) in zip(normalized_source, normalized_target):
        rows.append([-x, -y, -1.0, 0.0, 0.0, 0.0, u * x, u * y, u])
        rows.append([0.0, 0.0, 0.0, -x, -y, -1.0, v * x, v * y, v])

    design = np.asarray(rows, dtype=float)
    _, singular_values, vh = np.linalg.svd(design, full_matrices=True)
    # A non-degenerate planar calibration has rank 8. With exactly four pairs
    # there are only eight singular values, so s[-1] is the rank witness. With
    # more pairs the last value is the homogeneous null direction and s[-2]
    # measures whether rank 8 is present.
    threshold = np.finfo(float).eps * max(design.shape) * singular_values[0]
    rank_witness = singular_values[-1] if design.shape[0] == 8 else singular_values[-2]
    if rank_witness <= threshold:
        raise ValueError("degenerate correspondences")

    normalized_h = vh[-1].reshape(3, 3)
    source_transform_array = np.asarray(source_transform, dtype=float)
    target_inverse = np.linalg.inv(np.asarray(target_transform, dtype=float))
    denormalized = target_inverse @ normalized_h @ source_transform_array
    return _homogeneous_scale(denormalized)


def project_point(h: Sequence[Sequence[float]], p: Sequence[float]) -> Point:
    """Project a finite point through a homography."""
    if len(p) != 2:
        raise ValueError("point must be a pair")
    x, y = float(p[0]), float(p[1])
    if not (isfinite(x) and isfinite(y)):
        raise ValueError("point must be finite")
    matrix = np.asarray(h, dtype=float)
    if matrix.shape != (3, 3) or not np.isfinite(matrix).all():
        raise ValueError("homography must be a finite 3x3 matrix")
    denominator = float(matrix[2, 0] * x + matrix[2, 1] * y + matrix[2, 2])
    if abs(denominator) <= 1e-12:
        raise ValueError("point projects to infinity")
    return (
        float((matrix[0, 0] * x + matrix[0, 1] * y + matrix[0, 2]) / denominator),
        float((matrix[1, 0] * x + matrix[1, 1] * y + matrix[1, 2]) / denominator),
    )
