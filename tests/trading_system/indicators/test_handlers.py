import pytest

from tests.logger.empty_logger_mock import empty_logger_mock

from tests.trading_interface.trading_interface_mock import TradingInterfaceMock
from trading_system.trading_system import Handlers

from trading_system.indicators import *

one_values = [1] * 10
increasing_values = list(range(1, 11))
decreasing_values = list(reversed(increasing_values))
real_values = [10.2717, 10.295, 10.330, 10.332, 10.326, 10.303, 10.355, 10.341,
               10.277, 10.270, 10.256, 10.230, 10.270,
               10.247, 10.251, 10.263, 10.223, 10.220, 10.220, 10.257, 10.318,
               10.291, 10.297, 10.286, 10.289]

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


def check_results(handler_results: tp.List[tp.Any],
                  expected_results: tp.List[tp.Any]) -> None:
    assert len(handler_results) == len(expected_results)
    for handler_result, correct_result in zip(handler_results,
                                              expected_results):
        assert handler_result == pytest.approx(correct_result)


def simulate_handler(ti: TradingInterfaceMock,
                     handler: TradingSystemHandler) -> None:
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
def test_exp_moving_average_handler(values: tp.List[float],
                                    ti: TradingInterfaceMock,
                                    window_size: int,
                                    empty_logger_mock: empty_logger_mock) \
        -> None:
    """ Check equality with .calculate_from(). """
    handler = ExpMovingAverageHandler(ti, window_size)
    simulate_handler(ti, handler)

    mid_prices = list(
        map(lambda c: c.get_mid_price(), ti.get_last_n_candles(len(values))))
    check_results(
        handler.get_last_n_values(len(values)),
        [ExpMovingAverageHandler.calculate_from(mid_prices[0: i + 1],
                                                2 / (1 + window_size)) for i in
         range(len(mid_prices))]
    )


@pytest.mark.parametrize(
    "ti,short,long,average,expected_macd,expected_signal",
    [
        (ones_ti, 2, 4, 3, [0] * (len(one_values) - 4),
         [0] * (len(one_values) - 4)),
        (real_ti, 10, 10, 8, [0] * (len(real_values) - 10),
         [0] * (len(real_values) - 10)),
        (TradingInterfaceMock.from_price_values([1, 5, 7, 9]), 1, 2, 2, [1, 1],
         [2 / 3, 1]),
        # 2/3 instead of 1 because macd_values[-2:] returns [0, x] when len(macd_values) == 1
    ]
)
def test_moving_average_cd_handler(ti: TradingInterfaceMock, short: int,
                                   long: int, average: int,
                                   expected_macd: tp.List[float],
                                   expected_signal: tp.List[float],
                                   empty_logger_mock: empty_logger_mock) \
        -> None:
    handler = MovingAverageCDHandler(ti, short, long, average)
    simulate_handler(ti, handler)

    check_results(
        handler.get_last_n_values(len(expected_macd)),
        list(zip(expected_macd, expected_signal))
    )


@pytest.mark.parametrize("values,ti", all_samples.values())
@pytest.mark.parametrize("window_size", [5])
def test_moving_average_handler(values: tp.List[float],
                                ti: TradingInterfaceMock,
                                window_size: int,
                                empty_logger_mock: empty_logger_mock) -> None:
    """ Check equality with .calculate_from(). """
    handler = MovingAverageHandler(ti, window_size)
    simulate_handler(ti, handler)

    mid_prices = list(
        map(lambda c: c.get_mid_price(), ti.get_last_n_candles(len(values))))
    check_results(
        handler.get_last_n_values(len(values)),
        [MovingAverageHandler.calculate_from(mid_prices[i: i + window_size])
         for i in range(len(mid_prices) - window_size + 1)]
    )


@pytest.mark.parametrize("values,ti", all_samples.values())
@pytest.mark.parametrize("window_size", [5])
def test_relative_strength_index_handler(values: tp.List[float],
                                         ti: TradingInterfaceMock,
                                         window_size: int,
                                         empty_logger_mock: empty_logger_mock) \
        -> None:
    """ Check equality with .calculate_from(). """
    handler = RelativeStrengthIndexHandler(ti, window_size)
    simulate_handler(ti, handler)

    deltas = list(
        map(lambda c: c.get_delta(), ti.get_last_n_candles(len(values))))
    check_results(
        handler.get_last_n_values(len(values)),
        [RelativeStrengthIndexHandler.calculate_from(
            deltas[i: i + window_size])[1]
         for i in range(len(deltas) - window_size + 1)]
    )


@pytest.mark.parametrize("values,ti", all_samples.values())
@pytest.mark.parametrize("window_size", [5])
def test_weighted_moving_average_handler(values: tp.List[float],
                                         ti: TradingInterfaceMock,
                                         window_size: int,
                                         empty_logger_mock: empty_logger_mock) \
        -> None:
    """ Check equality with .calculate_from(). """
    handler = WeightedMovingAverageHandler(ti, window_size)
    simulate_handler(ti, handler)

    mid_prices = list(
        map(lambda c: c.get_mid_price(), ti.get_last_n_candles(len(values))))
    check_results(
        handler.get_last_n_values(len(values)),
        [WeightedMovingAverageHandler.calculate_from(
            mid_prices[i: i + window_size])
            for i in range(len(mid_prices) - window_size + 1)]
    )
