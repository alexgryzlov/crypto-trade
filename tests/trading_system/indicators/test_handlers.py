import pytest

from tests.logger.empty_logger_mock import empty_logger_mock

from tests.trading_interface.trading_interface_mock import TradingInterfaceMock
from trading_system.trading_system import Handlers

from trading_system.indicators import *


one_values = [1] * 10
increasing_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
decreasing_values = list(reversed(increasing_values))
real_values = [10.2717, 10.295706500000001, 10.3306, 10.332899999999999, 10.3265, 10.303550000000001, 10.3553,
               10.341750000000001, 10.2776315, 10.27005, 10.2567625, 10.2300535, 10.27045, 10.2478715, 10.2515, 10.2637,
               10.223600000000001, 10.2202, 10.22035, 10.2573, 10.31885, 10.29145, 10.2972, 10.2865, 10.289768500000001]

ones_ti = TradingInterfaceMock.from_price_values(one_values)
increasing_ti = TradingInterfaceMock.from_price_values(increasing_values)
decreasing_ti = TradingInterfaceMock.from_price_values(decreasing_values)
real_ti = TradingInterfaceMock.from_price_values(real_values)
all_samples = {
    'ones': (one_values, ones_ti),
    'increasing': (increasing_values, increasing_ti),
    'decreasing': (decreasing_values, decreasing_ti),
    'real': (real_values, real_ti),
}


def check_results(handler_results, expected_results):
    assert len(handler_results) == len(expected_results)
    for handler_result, correct_result in zip(handler_results, expected_results):
        assert handler_result == pytest.approx(correct_result)


def simulate_handler(ti: TradingInterfaceMock, handler: TradingSystemHandler):
    handlers = Handlers().add(handler)

    ti.refresh()
    while ti.is_alive():
        ti.update()
        for handler in handlers.values():
            handler.update()
            # False update
            if ti.get_timestamp() % 3 == 0:
                handler.update()


@pytest.mark.parametrize("values,ti", all_samples.values())
@pytest.mark.parametrize("window_size", [5])
def test_exp_moving_average_handler(values, ti: TradingInterfaceMock, window_size: int, empty_logger_mock):
    """ Check equality with .get_from(). """
    handler = ExpMovingAverageHandler(ti, window_size)
    simulate_handler(ti, handler)

    mid_prices = list(map(lambda c: c.get_mid_price(), ti.get_last_n_candles(len(values))))
    check_results(
        handler.get_last_n_values(len(values)),
        [ExpMovingAverageHandler.get_from(mid_prices[0: i + 1], 2 / (1 + window_size)) for i in range(len(mid_prices))]
    )


@pytest.mark.parametrize(
    "ti,short,long,average,expected_macd,expected_signal",
    [
        (ones_ti, 2, 4, 3, [0] * (len(one_values) - 4), [0] * (len(one_values) - 4)),
        (real_ti, 10, 10, 8, [0] * (len(real_values) - 10), [0] * (len(real_values) - 10)),
        (TradingInterfaceMock.from_price_values([1, 5, 7, 9]), 1, 2, 2, [1, 1], [2/3, 1]),
        # 2/3 instead of 1 because macd_values[-2:] returns [0, x] when len(macd_values) == 1
    ]
)
def test_moving_average_cd_handler(ti: TradingInterfaceMock, short: int, long: int, average: int, expected_macd,
                                   expected_signal, empty_logger_mock):
    handler = MovingAverageCDHandler(ti, short, long, average)
    simulate_handler(ti, handler)

    check_results(
        handler.get_last_n_values(len(expected_macd)),
        list(zip(expected_macd, expected_signal))
    )


@pytest.mark.parametrize("values,ti", all_samples.values())
@pytest.mark.parametrize("window_size", [5])
def test_moving_average_handler(values, ti: TradingInterfaceMock, window_size: int, empty_logger_mock):
    """ Check equality with .get_from(). """
    handler = MovingAverageHandler(ti, window_size)
    simulate_handler(ti, handler)

    mid_prices = list(map(lambda c: c.get_mid_price(), ti.get_last_n_candles(len(values))))
    check_results(
        handler.get_last_n_values(len(values)),
        [MovingAverageHandler.get_from(mid_prices[i: i + window_size])
         for i in range(len(mid_prices) - window_size + 1)]
    )


@pytest.mark.parametrize("values,ti", all_samples.values())
@pytest.mark.parametrize("window_size", [5])
def test_relative_strength_index_handler(values, ti: TradingInterfaceMock, window_size: int, empty_logger_mock):
    """ Check equality with .get_from(). """
    handler = RelativeStrengthIndexHandler(ti, window_size)
    simulate_handler(ti, handler)

    deltas = list(map(lambda c: c.get_delta(), ti.get_last_n_candles(len(values))))
    check_results(
        handler.get_last_n_values(len(values)),
        [RelativeStrengthIndexHandler.get_from(deltas[i: i + window_size])[1]
         for i in range(len(deltas) - window_size + 1)]
    )


@pytest.mark.parametrize("values,ti", all_samples.values())
@pytest.mark.parametrize("window_size", [5])
def test_weighted_moving_average_handler(values, ti: TradingInterfaceMock, window_size: int, empty_logger_mock):
    """ Check equality with .get_from(). """
    handler = WeightedMovingAverageHandler(ti, window_size)
    simulate_handler(ti, handler)

    mid_prices = list(map(lambda c: c.get_mid_price(), ti.get_last_n_candles(len(values))))
    check_results(
        handler.get_last_n_values(len(values)),
        [WeightedMovingAverageHandler.get_from(mid_prices[i: i + window_size])
         for i in range(len(mid_prices) - window_size + 1)]
    )
