from accumulation_distribution_handler import AccumulationDistributionHandler
from on_balance_volume_handler import OnBalanceVolumeHandler
from volume_relative_strength_index_handler import VolumeRelativeStrengthIndexHandler
from trading.candle import Candle

import typing as tp

import pytest
import dataclasses


@dataclasses.dataclass
class CandlesAndResult:
    candles: tp.List[Candle]
    result: tp.List[float]


AD_TEST_CASES = [
    CandlesAndResult(
        candles=[Candle(0, 0, 62.15, 61.37, 62.34, 7849), Candle(0, 0, 60.81, 60.69, 62.05, 11692),
                 Candle(0, 0, 60.45, 60.1, 62.27, 10575), Candle(0, 0, 59.18, 58.61, 60.79, 13059),
                 Candle(0, 0, 59.24, 58.71, 59.93, 20734), Candle(0, 0, 60.2, 59.86, 61.75, 29630),
                 Candle(0, 0, 58.48, 57.97, 60.00, 17705), Candle(0, 0, 58.24, 58.02, 59.00, 7259),
                 Candle(0, 0, 57.48, 61.37, 59.07, 10475), Candle(0, 0, 58.65, 58.3, 59.22, 5204)],
        result=[4774, -4855, -12019, -18249, -21006, -39976, -48785, -52785, -47216, -48561])
]

OBV_TEST_CASES = [
    CandlesAndResult(
        candles=[Candle(0, 0, 10, 0, 0, 25200), Candle(0, 0, 10.15, 0, 0, 30000),
                 Candle(0, 0, 10.17, 0, 0, 25600), Candle(0, 0, 10.13, 0, 0, 32000),
                 Candle(0, 0, 10.11, 0, 0, 23000), Candle(0, 0, 10.15, 0, 0, 40000),
                 Candle(0, 0, 10.20, 0, 0, 36000), Candle(0, 0, 10.20, 0, 0, 20500),
                 Candle(0, 0, 10.22, 0, 0, 23000), Candle(0, 0, 10.21, 0, 0, 27500)],
        result=[0, 30000, 55600, 23600, 600, 40600, 76600, 76600, 99600, 72100])
]

VRSI_TEST_CASES = [
    CandlesAndResult(
        candles=[Candle(0, 61.42, 62.15, 61.37, 62.34, 7849), Candle(0, 62.15, 60.81, 60.69, 62.05, 11692),
                 Candle(0, 60.81, 60.45, 60.10, 62.27, 10575), Candle(0, 60.45, 59.18, 58.61, 60.79, 13059),
                 Candle(0, 59.18, 59.24, 58.71, 59.93, 20734), Candle(0, 59.24, 60.2, 59.86, 61.75, 29630),
                 Candle(0, 58.23, 58.48, 57.97, 60.00, 17705), Candle(0, 58.48, 58.24, 58.02, 59.00, 7259),
                 Candle(0, 58.24, 57.48, 61.37, 59.07, 10475), Candle(0, 57.48, 58.65, 58.3, 59.22, 5204)],
        result=[18.17, 36.98, 68.06, 83.9, 90.36, 72.74, 56.36])
]


@pytest.mark.parametrize('test', AD_TEST_CASES, ids=str)
def test_accumulation_distribution_formula(test: CandlesAndResult) -> None:
    assert AccumulationDistributionHandler.calculate_from(test.candles) == pytest.approx(test.result, 1)


@pytest.mark.parametrize('test', OBV_TEST_CASES, ids=str)
def test_on_balance_volume_formula(test: CandlesAndResult) -> None:
    assert OnBalanceVolumeHandler.calculate_from(test.candles) == pytest.approx(test.result, 1)


@pytest.mark.parametrize('test', VRSI_TEST_CASES, ids=str)
def test_volume_rsi_formula(test: CandlesAndResult) -> None:
    assert VolumeRelativeStrengthIndexHandler.calculate_from(test.candles, window_size=4) == pytest.approx(test.result,
                                                                                                           1)
