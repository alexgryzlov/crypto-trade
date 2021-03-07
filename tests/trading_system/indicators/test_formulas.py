import pytest
from trading_system.indicators import *


increasing_values = [10., 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 11.]
decreasing_values = list(reversed(increasing_values))
factorial_values = [120, 60, 40, 30, 24]  # 5! / 1, 5! / 2, ...
one_values = [1 for _ in range(10)]


def _get_deltas(values):
    deltas = []
    for i in range(len(values) - 1):
        deltas.append(values[i + 1] - values[i])
    return deltas


@pytest.mark.parametrize(
    "values,alpha,expected",
    [
        (increasing_values, 1, increasing_values[-1]),
        (one_values, 0.95, 1),
    ]
)
def test_exp_moving_average(values, alpha, expected):
    assert ExpMovingAverageHandler.get_from(values, 1) == pytest.approx(expected)


@pytest.mark.parametrize(
    "values,expected",
    [
        (one_values, 1),
        (increasing_values, 10.5),
        (decreasing_values, 10.5),
    ]
)
def test_moving_average(values, expected):
    assert MovingAverageHandler.get_from(values) == pytest.approx(expected)


@pytest.mark.parametrize(
    "deltas,alpha,expected_rs,expected_rsi",
    [
        (_get_deltas(one_values), None, 1, 50),
        (_get_deltas(increasing_values), None, float('inf'), 100),
        (_get_deltas(decreasing_values), None, 0, 0),
        ([1, -1], 2 / 3, 0.5, 100 / 3),
    ]
)
def test_relative_strength_index(deltas, alpha, expected_rs, expected_rsi):
    rs, rsi = RelativeStrengthIndexHandler.get_from(deltas, alpha)
    assert rs == pytest.approx(expected_rs)
    assert rsi == pytest.approx(expected_rsi)


@pytest.mark.parametrize(
    "values,expected",
    [
        (one_values, 1),
        (factorial_values, 600 / 15),  # 5 * 5! / sum(1..5)
    ]
)
def test_weighted_moving_average(values, expected):
    assert WeightedMovingAverageHandler.get_from(values) == pytest.approx(expected)
