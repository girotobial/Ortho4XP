import src.geo as geo
import math

import pytest


@pytest.mark.parametrize(
    ("degrees", "expected"),
    [
        (-45, -math.pi / 4),
        (0, 0),
        (90, math.pi / 2),
        (180, math.pi),
        (270, 3 / 2 * math.pi),
        (360, 2 * math.pi),
    ],
)
def test_radians(degrees, expected):
    assert geo.radians(degrees) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("lattitude", "expected"),
    [(0, 111319.49), (90, 0), (45, 78714.77), (60, 55659.75)],
)
def test_meters_per_degree_longitude(lattitude, expected):
    assert geo.meters_per_degree_longitude(lattitude) == pytest.approx(
        expected
    )


@pytest.mark.parametrize(
    ("lattitude", "expected"),
    [
        (90, float("inf")),
        (0, 8.98315e-6),
        (45, 1.27041e-5),
        (60, 1.79663e-5),
        (89, 5.14723e-4),
    ],
)
def test_degrees_longitude_per_meter(lattitude, expected):
    assert geo.degrees_longitude_per_meter(lattitude) == pytest.approx(
        expected
    )
