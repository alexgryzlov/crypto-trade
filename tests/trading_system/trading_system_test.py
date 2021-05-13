import pytest
from mock import MagicMock

from helpers.typing.common_types import ConfigsScope

from tests.logger.empty_logger_mock import empty_logger_mock
from tests.trading_interface.trading_interface_mock import TradingInterfaceMock
from tests.configs import base_config

from trading_system.trading_system import TradingSystem
from trading import AssetPair, Asset, Direction

one_values = [1] * 10
real_values = [10.2717, 10.295, 10.330, 10.332, 10.326, 10.303, 10.355, 10.341,
               10.277, 10.270, 10.256, 10.230, 10.270,
               10.247, 10.251, 10.263, 10.223, 10.220, 10.220, 10.257, 10.318,
               10.291, 10.297, 10.286, 10.289]

ones_ti = TradingInterfaceMock.from_price_values(one_values)
real_ti = TradingInterfaceMock.from_price_values(real_values)
ones_ti.order_is_filled = MagicMock(return_value=True)
real_ti.order_is_filled = MagicMock(return_value=True)


@pytest.fixture
def ts(request, base_config: ConfigsScope, empty_logger_mock: empty_logger_mock) -> TradingSystem:
    return TradingSystem(request.param, config=base_config['trading_system'])


@pytest.mark.parametrize('ts', [ones_ti], indirect=True)
@pytest.mark.parametrize('ti', [ones_ti])
def test_trading_system_buy(ti: TradingInterfaceMock, ts: TradingSystem, empty_logger_mock):
    assert ts.exchange_is_alive() is ti.is_alive()
    initial_balance = ts.get_balance()
    ts.buy(AssetPair(Asset('WAVES'), Asset('USDN')), 1, 10)
    assert len(ts.get_active_orders()) == 1
    ts.update()
    assert len(ts.get_active_orders()) == 0
    assert ts.get_balance() + 10 == initial_balance
    assert ts._wallet[Asset('WAVES')] == 11


@pytest.mark.parametrize('ts', [ones_ti], indirect=True)
@pytest.mark.parametrize('ti', [ones_ti])
def test_trading_system_sell(ti: TradingInterfaceMock, ts: TradingSystem, empty_logger_mock):
    initial_balance = ts.get_balance()
    ts.sell(AssetPair(Asset('WAVES'), Asset('USDN')), 1, 10)
    assert len(ts.get_active_orders()) == 1
    ts.update()
    assert len(ts.get_active_orders()) == 0
    assert ts.get_balance() == initial_balance + 10
    assert ts._wallet[Asset('WAVES')] == 9


@pytest.mark.parametrize('ts', [ones_ti], indirect=True)
@pytest.mark.parametrize('ti', [ones_ti])
def test_trading_system_cancel(ti: TradingInterfaceMock, ts: TradingSystem, empty_logger_mock):
    initial_balance = ts.get_balance()
    ts.sell(AssetPair(Asset('WAVES'), Asset('USDN')), 1, 10)
    assert len(ts.get_active_orders()) == 1
    ts.cancel_all()
    assert len(ts.get_active_orders()) == 0
    ts.update()
    assert ts.get_balance() == initial_balance


@pytest.mark.parametrize('ts', [ones_ti], indirect=True)
@pytest.mark.parametrize('ti', [ones_ti])
def test_trading_system_filled_signal(ti: TradingInterfaceMock, ts: TradingSystem, empty_logger_mock):
    assert ts.get_price_by_direction(Direction.BUY) == ts.get_buy_price()
    assert ts.get_price_by_direction(Direction.SELL) == ts.get_sell_price()

    ts.buy(AssetPair(Asset('WAVES'), Asset('USDN')), 1, 10)
    ts.buy(AssetPair(Asset('WAVES'), Asset('USDN')), 1, 10)
    ts.update()

    signals = ts.get_trading_signals()
    assert len(ts.get_trading_signals()) == 0
    assert len(signals) >= 2
    assert any(x.name == 'filled_order' for x in signals)


@pytest.mark.parametrize('ts', [ones_ti], indirect=True)
@pytest.mark.parametrize('ti', [ones_ti])
def test_get_total_balance(ti: TradingInterfaceMock, ts: TradingSystem, empty_logger_mock):
    ti.update()


@pytest.mark.parametrize('ts', [ones_ti], indirect=True)
@pytest.mark.parametrize('ti', [ones_ti])
def test_trading_system_stop_trading(ti: TradingInterfaceMock, ts: TradingSystem, empty_logger_mock):
    ti.update()
    init_balance = 30
    ts._wallet[Asset('USDN')] = init_balance
    ts._wallet[Asset('WAVES')] = 0
    ts.buy(AssetPair(Asset('WAVES'), Asset('USDN')), 1, 10)
    ts.buy(AssetPair(Asset('WAVES'), Asset('USDN')), 1, 10)
    assert ts._wallet[Asset('USDN')] == init_balance - 20
    assert len(ts.get_active_orders()) == 2
    ts.stop_trading()
    ts.update()
    assert len(ts.get_active_orders()) == 0
    assert ts._wallet[Asset('USDN')] == init_balance


@pytest.mark.parametrize('ts', [real_ti], indirect=True)
@pytest.mark.parametrize('ti', [real_ti])
def test_trading_system_get_total_balance(ti: TradingInterfaceMock, ts: TradingSystem, empty_logger_mock):
    ti.update()
    init_balance_usdn = 100
    init_balance_waves = 10
    ts._wallet[Asset('USDN')] = init_balance_usdn
    ts._wallet[Asset('WAVES')] = init_balance_waves
    assert pytest.approx(ts.get_total_balance(), 1e-6) == \
           (init_balance_usdn + init_balance_waves * ts.get_price_by_direction(Direction.SELL))
    ts.sell(AssetPair(Asset('WAVES'), Asset('USDN')), 10, 10)
    ts.update()
    assert pytest.approx(ts.get_total_balance(), 1e-6) == init_balance_usdn + 10 * 10
    ts.buy(AssetPair(Asset('WAVES'), Asset('USDN')), 20, 10)
    ts.update()
    ti.update()
    ti.update()
    assert pytest.approx(ts.get_total_balance(), 1e-6) == \
           (20 * ts.get_price_by_direction(Direction.SELL))
