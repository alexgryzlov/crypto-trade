import unittest
from trading_system.indicators import *


class TestIndicatorsGetFrom(unittest.TestCase):
    """ For testing formulas. """
    @staticmethod
    def _get_deltas(values):
        deltas = []
        for i in range(len(values) - 1):
            deltas.append(values[i + 1] - values[i])
        return deltas

    def setUp(self):
        self.increasing_values = [10., 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 11.]
        self.decreasing_values = list(reversed(self.increasing_values))
        self.factorial_values = [120, 60, 40, 30, 24]  # 5! / 1, 5! / 2, ...
        self.one_values = [1 for _ in range(10)]

    def test_exp_moving_average(self):
        self.assertAlmostEqual(ExpMovingAverageHandler.get_from(self.one_values, 0.95), 1)
        self.assertAlmostEqual(
            ExpMovingAverageHandler.get_from(self.increasing_values, 1),
            self.increasing_values[-1]  # 1 - alpha = 0
        )

    def test_moving_average(self):
        self.assertAlmostEqual(MovingAverageHandler.get_from(self.one_values), 1)
        self.assertAlmostEqual(MovingAverageHandler.get_from(self.increasing_values), 10.5)
        self.assertAlmostEqual(MovingAverageHandler.get_from(self.decreasing_values), 10.5)

    def test_relative_strength_index(self):
        rs, rsi = RelativeStrengthIndexHandler.get_from(self._get_deltas(self.one_values))
        self.assertAlmostEqual(rs, 1)
        self.assertAlmostEqual(rsi, 50)
        rs, rsi = RelativeStrengthIndexHandler.get_from(self._get_deltas(self.increasing_values))
        self.assertAlmostEqual(rs, float('inf'))
        self.assertAlmostEqual(rsi, 100)
        rs, rsi = RelativeStrengthIndexHandler.get_from(self._get_deltas(self.decreasing_values))
        self.assertAlmostEqual(rs, 0)
        self.assertAlmostEqual(rsi, 0)
        rs, rsi = RelativeStrengthIndexHandler.get_from([1, -1], alpha=1/2)
        self.assertAlmostEqual(rs, 0.5)
        self.assertAlmostEqual(rsi, 100 / 3)

    def test_weighted_moving_average(self):
        self.assertAlmostEqual(WeightedMovingAverageHandler.get_from(self.one_values), 1)
        self.assertAlmostEqual(
            WeightedMovingAverageHandler.get_from(self.factorial_values),
            600 / 15  # 5 * 5! / C_5^2
        )
