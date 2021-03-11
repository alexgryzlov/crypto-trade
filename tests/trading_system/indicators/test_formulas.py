import pytest
from trading_system.indicators import *

increasing_values = [10., 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9,
                     11.]
decreasing_values = list(reversed(increasing_values))
factorial_values = [120, 60, 40, 30, 24]  # 5! / 1, 5! / 2, ...
one_values = [1] * 10


@pytest.mark.parametrize(
    "values,alpha,expected",
    [
        (increasing_values, 1, increasing_values[-1]),
        (one_values, 0.95, 1),
    ]
)
def test_exp_moving_average(values: tp.List[float], alpha: float,
                            expected: float) -> None:
    assert ExpMovingAverageHandler.calculate_from(values, 1) == pytest.approx(
        expected)


@pytest.mark.parametrize(
    "values,expected",
    [
        (one_values, 1),
        (increasing_values, 10.5),
        (decreasing_values, 10.5),
    ]
)
def test_moving_average(values: tp.List[float], expected: float) -> None:
    assert MovingAverageHandler.calculate_from(values) == pytest.approx(
        expected)


@pytest.mark.parametrize(
    "deltas,alpha,expected_rs,expected_rsi",
    [
        (np.diff(one_values), None, 1, 50),
        (np.diff(increasing_values), None, float('inf'), 100),
        (np.diff(decreasing_values), None, 0, 0),
        ([1, -1], 2 / 3, 0.5, 100 / 3),
    ]
)
def test_relative_strength_index(deltas: tp.List[float],
                                 alpha: tp.Optional[float],
                                 expected_rs: float,
                                 expected_rsi: float) -> None:
    rs, rsi = RelativeStrengthIndexHandler.calculate_from(deltas, alpha)
    assert rs == pytest.approx(expected_rs)
    assert rsi == pytest.approx(expected_rsi)


@pytest.mark.parametrize(
    "values,expected",
    [
        (one_values, 1),
        (factorial_values, 600 / 15),  # 5 * 5! / sum(1..5)
    ]
)
def test_weighted_moving_average(values: tp.List[float],
                                 expected: float) -> None:
    assert WeightedMovingAverageHandler.calculate_from(
        values) == pytest.approx(expected)
