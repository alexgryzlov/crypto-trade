import pytest
import numpy as np

from trading_interface.simulator.price_simulator import PriceSimulator, \
    PriceSimulatorType
from trading.candle import Candle

from tests.logger.empty_logger_mock import empty_logger_mock


def test_three_interval_big_random(
        empty_logger_mock: empty_logger_mock) -> None:
    for lifetime in range(4, 25):
        ps = PriceSimulator(lifetime, PriceSimulatorType.ThreeIntervalPath)
        for i in range(500):
            vals = sorted(np.random.random(4))
            candle_up = Candle(i, vals[1], vals[2], vals[0], vals[3], 1)
            candle_down = Candle(i, vals[2], vals[1], vals[0], vals[3], 1)
            htl = ps._high_to_low(candle_up)
            lth = ps._low_to_high(candle_up)
            assert (len(lth) == lifetime and len(htl) == lifetime)
            assert (htl[1] >= htl[0])
            assert (lth[1] <= lth[0])
            assert all([i in htl and i in lth for i in vals])

            htl = ps._high_to_low(candle_down)
            lth = ps._low_to_high(candle_down)
            assert (len(lth) == lifetime and len(htl) == lifetime)
            assert (htl[1] >= htl[0])
            assert (lth[1] <= lth[0])
            assert all([i in htl and i in lth for i in vals])

            htl_noise = ps._high_to_low(candle_up, np.random.normal)
            lth_noise = ps._low_to_high(candle_up, np.random.normal)
            assert (candle_up.low == min(*htl_noise) and
                    candle_up.low == min(*lth_noise))
            assert (candle_up.high == max(*htl_noise) and
                    candle_up.high == max(*lth_noise))
            assert all([i in htl and i in lth for i in vals])


def test_different_directions(empty_logger_mock: empty_logger_mock) -> None:
    candles_lifetime = 25
    ps = PriceSimulator(candles_lifetime, PriceSimulatorType.ThreeIntervalPath)
    candles = [Candle(i, 1, 2, 0, 5, 1) for i in range(1000)]
    up = [[ps.get_price(candle, i) for i in range(candles_lifetime)]
          for candle in candles if hash(candle) % 2 == 0]
    down = [[ps.get_price(candle, i) for i in range(candles_lifetime)]
            for candle in candles if hash(candle) % 2 == 1]
    assert (up.count(up[0]) == len(up) and down.count(down[0]) == len(down))
    assert (up[0] != down[0])


def test_multi_interval_big_random(
        empty_logger_mock: empty_logger_mock) -> None:
    candles_lifetime = 25
    total_steps = 2000
    ps = PriceSimulator(candles_lifetime, PriceSimulatorType.ThreeIntervalPath)
    for i in range(100):
        intervals = [[np.random.uniform(0, 10), np.random.uniform(0, 10)]]
        for j in range(1000):
            intervals.append([intervals[-1][1], np.random.uniform(0, 10)])
        path = ps._build_multi_interval_path(intervals, total_steps)
        assert (len(path) == total_steps)


@pytest.mark.parametrize("candles_lifetime", [25])
@pytest.mark.parametrize("total_steps", [100])
def test_same_values(candles_lifetime: int, total_steps: int,
                     empty_logger_mock: empty_logger_mock) -> None:
    ps = PriceSimulator(candles_lifetime, PriceSimulatorType.ThreeIntervalPath)
    intervals = [[1, 1], [1, 1], [1, 1]]
    res = ps._build_multi_interval_path(intervals, total_steps)
    print(res)
    assert isinstance(res, list)
    assert len(res) == total_steps
