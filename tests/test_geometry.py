import numpy as np
import pytest

from rangyuu.geometry import homography_dlt, project_point


def assert_maps(h, source, destination, atol=1e-8):
    for point, expected in zip(source, destination):
        assert np.allclose(project_point(h, point), expected, atol=atol, rtol=1e-8)


def test_identity_with_more_than_four_points():
    points = [(0, 0), (2, 0), (3, 1), (2, 3), (0, 2), (1, 1)]
    assert_maps(homography_dlt(points, points), points, points)


def test_valid_zero_h33_transform():
    source = [(1, 0), (2, 1), (3, 1), (1, 2), (4, 3)]
    destination = [(1, 0), (1, 0.5), (1, 1 / 3), (1, 2), (1, 0.75)]
    h = homography_dlt(source, destination)
    assert abs(h[2][2]) < 1e-8
    assert_maps(h, source, destination)


def test_extreme_coordinate_scale():
    source = [(1e6, 2e6), (3e6, 2e6), (3e6, 5e6), (1e6, 5e6), (2e6, 3e6)]
    destination = [(0, 0), (4, 0), (4, 6), (0, 6), (2, 2)]
    assert_maps(homography_dlt(source, destination), source, destination, atol=1e-7)


@pytest.mark.parametrize(
    "source,destination",
    [
        ([(0, 0), (1, 0), (2, 0), (3, 0)], [(0, 0), (1, 0), (2, 0), (3, 0)]),
        ([(0, 0), (1, 0), (1, 1), (0, 1)], [(0, 0), (1, 0), (2, 0), (3, 0)]),
    ],
)
def test_degenerate_source_or_destination_rejected(source, destination):
    with pytest.raises(ValueError, match="degenerate"):
        homography_dlt(source, destination)
