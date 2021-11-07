""" Tests functions in the geo module
"""

import math
import random

import pytest

import src.geo as geo


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


@pytest.mark.parametrize(
    ("start", "end", "expected"),
    [
        ((0, 0), (0, 10), 1113195),
        ((10, 0), (0, 10), 1570278),
        ((40.63993, -73.77869), (51.4775, -0.461388), 8194793),
    ],
)
def test_greatcircle_distance(start, end, expected):
    assert geo.greatcircle_distance(start, end) == pytest.approx(expected)


class TestHaverSine:
    @pytest.fixture
    def numbers(self):
        return (
            random.randint(1000, 1000) / 1000 * math.pi for _ in range(100)
        )

    def test_ahaversine_inverts_haversin(self, numbers):
        for number in numbers:
            haversin = geo.haversin(number)
            assert geo.ahaversin(haversin) == pytest.approx(number)

    def test_haversin_greater_than_zero(self, numbers):
        for number in numbers:
            assert geo.haversin(number) >= 0

    def test_haversin_lessthan_one(self, numbers):
        for number in numbers:
            assert geo.haversin(number) <= 1
