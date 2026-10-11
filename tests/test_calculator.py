import math

import pytest

from rainwise.calculator import (
    LARGEST_TANK_LITRES,
    STANDARD_TANKS_LITRES,
    ValidationError,
    calculate,
    format_litres,
    recommend_tank,
)


def test_reference_example_is_8000_litres():
    r = calculate(200, 50, 80)
    assert r["harvestable_litres"] == 8000
    assert r["harvestable_kl"] == 8.0
    assert r["recommended_tank_litres"] == 10_000
    assert r["capacity_exceeded"] is False
    assert "8,000 litres" in r["message"]


def test_result_is_computed_from_inputs_not_hardcoded():
    r = calculate(33.3, 12.7, 66.6)
    assert r["harvestable_litres"] == pytest.approx(33.3 * 12.7 * 66.6 / 100, abs=0.01)
    assert calculate(100, 10, 100)["harvestable_litres"] == 1000


def test_zero_rainfall_gives_zero_and_no_tank():
    r = calculate(200, 0, 80)
    assert r["harvestable_litres"] == 0
    assert r["recommended_tank_litres"] is None
    assert r["capacity_exceeded"] is False
    assert "no rainfall" in r["message"]


def test_zero_efficiency_is_accepted_and_gives_zero():
    r = calculate(200, 50, 0)
    assert r["harvestable_litres"] == 0
    assert r["recommended_tank_litres"] is None
    assert "0% collection efficiency" in r["message"]


@pytest.mark.parametrize("area", [-1, -0.001, 0])
def test_non_positive_roof_area_rejected(area):
    with pytest.raises(ValidationError):
        calculate(area, 50, 80)


@pytest.mark.parametrize("rain", [-5, float("nan"), float("inf"), "abc", None, True])
def test_invalid_rainfall_rejected(rain):
    with pytest.raises(ValidationError):
        calculate(200, rain, 80)


@pytest.mark.parametrize("eff", [-1, 100.5, 150, float("nan"), "80", None])
def test_efficiency_outside_range_rejected(eff):
    with pytest.raises(ValidationError):
        calculate(200, 50, eff)


def test_all_errors_are_reported_together():
    with pytest.raises(ValidationError) as exc:
        calculate(-1, -1, 500)
    assert len(exc.value.errors) == 3


def test_result_above_largest_tank_flags_multiple_tanks():
    r = calculate(1000, 50, 100)  # 50,000 L
    assert r["harvestable_litres"] == 50_000
    assert r["recommended_tank_litres"] is None
    assert r["capacity_exceeded"] is True
    assert r["largest_tanks_needed"] == math.ceil(50_000 / LARGEST_TANK_LITRES) == 3
    assert "larger storage system" in r["recommendation"]


@pytest.mark.parametrize(
    "litres,expected",
    [
        (0.01, 500),
        (500, 500),
        (500.01, 1_000),
        (1_000, 1_000),
        (1_999, 2_000),
        (2_001, 5_000),
        (5_000, 5_000),
        (8_000, 10_000),
        (10_000, 10_000),
        (10_001, 20_000),
        (20_000, 20_000),
        (20_000.01, None),
        (0, None),
    ],
)
def test_tank_recommendation_boundaries(litres, expected):
    assert recommend_tank(litres) == expected


def test_standard_tank_sizes():
    assert STANDARD_TANKS_LITRES == (500, 1_000, 2_000, 5_000, 10_000, 20_000)


def test_exactly_largest_tank_is_not_flagged_as_exceeded():
    r = calculate(400, 50, 100)  # 20,000 L
    assert r["recommended_tank_litres"] == 20_000
    assert r["capacity_exceeded"] is False


def test_format_litres():
    assert format_litres(8000.0) == "8,000"
    assert format_litres(1234.5) == "1,234.5"
    assert format_litres(0) == "0"
