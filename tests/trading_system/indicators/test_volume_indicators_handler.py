from trading_system.indicators import *
from trading_system.indicators.accumulation_distribution_handler import AccumulationDistributionHandler
from trading_system.indicators.on_balance_volume_handler import OnBalanceVolumeHandler
from trading_system.indicators.volume_relative_strength_index_handler import VolumeRelativeStrengthIndexHandler
from test_volume_indicators_formulas import AD_TEST_CASES, OBV_TEST_CASES, VRSI_TEST_CASES
from tests.trading_interface.trading_interface_mock import TradingInterfaceMock

from trading.candle import Candle

import typing as tp

import pytest


def simulate_handler(handler: TradingSystemHandler):
    handler.ti.refresh()
    while handler.ti.is_alive():
        handler.ti.update()
        handler.update()
        # False update
        if handler.ti.get_timestamp() % 3 == 0:
            handler.update()


@pytest.mark.parametrize("candles, result", AD_TEST_CASES)
def test_accumulation_handler(candles: tp.List[Candle], result: tp.List[float]):
    ti = TradingInterfaceMock(candles)
    handler = AccumulationDistributionHandler(ti)
    simulate_handler(handler)
    assert handler.get_last_n_values(len(candles)) == pytest.approx(result, abs=1e-2)


@pytest.mark.parametrize("candles, result", OBV_TEST_CASES)
def test_on_balance_volume_handler(candles: tp.List[Candle], result: tp.List[float]):
    ti = TradingInterfaceMock(candles)
    handler = OnBalanceVolumeHandler(ti)
    simulate_handler(handler)
    assert handler.get_last_n_values(len(candles)) == pytest.approx(result, abs=1e-2)


@pytest.mark.parametrize("candles, result", VRSI_TEST_CASES)
def test_relative_strength_index_handler(candles: tp.List[Candle], result: tp.List[float]):
    ti = TradingInterfaceMock(candles)
    handler = VolumeRelativeStrengthIndexHandler(ti, window_size=4)
    simulate_handler(handler)
    assert handler.get_last_n_values(len(candles)) == pytest.approx(result, abs=1e-2)
