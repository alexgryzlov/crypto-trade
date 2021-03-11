from trading_system.indicators.accumulation_distribution_handler import AccumulationDistributionHandler
from trading_system.indicators.on_balance_volume_handler import OnBalanceVolumeHandler
from trading_system.indicators.volume_relative_strength_index_handler import VolumeRelativeStrengthIndexHandler
from trading.candle import Candle

import typing as tp

import pytest

AD_TEST_CASES = [
    ([Candle(0, 0, 62.15, 61.37, 62.34, 7849), Candle(0, 0, 60.81, 60.69, 62.05, 11692),
      Candle(0, 0, 60.45, 60.1, 62.27, 10575), Candle(0, 0, 59.18, 58.61, 60.79, 13059),
      Candle(0, 0, 59.24, 58.71, 59.93, 20734), Candle(0, 0, 60.2, 59.86, 61.75, 29630),
      Candle(0, 0, 58.48, 57.97, 60.00, 17705), Candle(0, 0, 58.24, 58.02, 59.00, 7259),
      Candle(0, 0, 58.69, 57.48, 59.07, 10475), Candle(0, 0, 58.65, 58.3, 59.22, 5204)],
     [4774.13, -4854.57, -12018.28, -18248.26, -20967.47, -39936.94, -48745.83, -52745.69, -47277.61, -48522.04])
]

OBV_TEST_CASES = [
    ([Candle(0, 0, 10, 0, 0, 25200), Candle(0, 0, 10.15, 0, 0, 30000),
      Candle(0, 0, 10.17, 0, 0, 25600), Candle(0, 0, 10.13, 0, 0, 32000),
      Candle(0, 0, 10.11, 0, 0, 23000), Candle(0, 0, 10.15, 0, 0, 40000),
      Candle(0, 0, 10.20, 0, 0, 36000), Candle(0, 0, 10.20, 0, 0, 20500),
      Candle(0, 0, 10.22, 0, 0, 23000), Candle(0, 0, 10.21, 0, 0, 27500)],
     [0, 30000, 55600, 23600, 600, 40600, 76600, 76600, 99600, 72100])
]

VRSI_TEST_CASES = [
    ([Candle(0, 61.42, 62.15, 61.37, 62.34, 7849), Candle(0, 62.15, 60.81, 60.69, 62.05, 11692),
      Candle(0, 60.81, 60.45, 60.10, 62.27, 10575), Candle(0, 60.45, 59.18, 58.61, 60.79, 13059),
      Candle(0, 59.18, 59.24, 58.71, 59.93, 20734), Candle(0, 59.24, 60.2, 59.86, 61.75, 29630),
      Candle(0, 58.23, 58.48, 57.97, 60.00, 17705), Candle(0, 58.48, 58.24, 58.02, 59.00, 7259),
      Candle(0, 58.24, 57.48, 61.37, 59.07, 10475), Candle(0, 57.48, 58.65, 58.3, 59.22, 5204)],
     [18.17, 36.98, 68.06, 83.9, 90.36, 72.74, 56.36])
]


@pytest.mark.parametrize('candles, result', AD_TEST_CASES)
def test_accumulation_distribution_formula(candles: tp.List[Candle], result: tp.List[float]) -> None:
    assert AccumulationDistributionHandler.calculate_from(candles) == pytest.approx(result, abs=1e-2)


@pytest.mark.parametrize('candles, result', OBV_TEST_CASES)
def test_on_balance_volume_formula(candles: tp.List[Candle], result: tp.List[float]) -> None:
    assert OnBalanceVolumeHandler.calculate_from(candles) == pytest.approx(result, abs=1e-2)


@pytest.mark.parametrize('candles, result', VRSI_TEST_CASES)
def test_volume_rsi_formula(candles: tp.List[Candle], result: tp.List[float]) -> None:
    print("HERE ", VolumeRelativeStrengthIndexHandler.calculate_from(candles, window_size=4))
    assert VolumeRelativeStrengthIndexHandler.calculate_from(candles, window_size=4) == pytest.approx(result, abs=1e-2)
