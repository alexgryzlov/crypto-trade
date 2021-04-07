import pytest
from mock import MagicMock

from tests.logger.empty_logger_mock import empty_logger_mock

from tests.trading_interface.trading_interface_mock import TradingInterfaceMock
from trading_system.trading_system import Handlers, TradingSystem
from trading import Order, AssetPair, Asset, Direction

one_values = [1] * 10
ones_ti = TradingInterfaceMock.from_price_values(one_values)
ones_ti.order_is_filled = MagicMock(return_value=True)


@pytest.fixture
def ts(request) -> TradingSystem:
    return TradingSystem(request.param, config={"currency_asset": "USDN", "wallet": {"USDN": 999999.0, "WAVES": 10.0}})


@pytest.mark.parametrize('ts', [ones_ti], indirect=True)
@pytest.mark.parametrize('ti', [ones_ti])
def test_trading_system_buy(ti: TradingInterfaceMock, ts, empty_logger_mock):
    assert ts.exchange_is_alive() is ti.is_alive()
    initial_balance = ts.get_balance()
    ts.buy(AssetPair(Asset("USDN"), Asset("WAVES")), 1, 10)
    assert len(ts.get_active_orders()) == 1
    ts.update()
    assert len(ts.get_active_orders()) == 0
    assert ts.get_balance() + 10 == initial_balance
    assert ts.wallet[Asset("WAVES")] == 11


@pytest.mark.parametrize('ts', [ones_ti], indirect=True)
@pytest.mark.parametrize('ti', [ones_ti])
def test_trading_system_sell(ti: TradingInterfaceMock, ts, empty_logger_mock):
    initial_balance = ts.get_balance()
    ts.sell(AssetPair(Asset("USDN"), Asset("WAVES")), 1, 10)
    assert len(ts.get_active_orders()) == 1
    ts.update()
    assert len(ts.get_active_orders()) == 0
    assert ts.get_balance() == initial_balance + 10
    assert ts.wallet[Asset("WAVES")] == 9


@pytest.mark.parametrize('ts', [ones_ti], indirect=True)
@pytest.mark.parametrize('ti', [ones_ti])
def test_trading_system_cancel(ti: TradingInterfaceMock, ts, empty_logger_mock):
    initial_balance = ts.get_balance()
    ts.sell(AssetPair(Asset("USDN"), Asset("WAVES")), 1, 10)
    assert len(ts.get_active_orders()) == 1
    ts.cancel_all()
    assert len(ts.get_active_orders()) == 0
    ts.update()
    assert ts.get_balance() == initial_balance


@pytest.mark.parametrize('ts', [ones_ti], indirect=True)
@pytest.mark.parametrize('ti', [ones_ti])
def test_trading_system_filled_signal(ti: TradingInterfaceMock, ts, empty_logger_mock):
    assert ts.get_price_by_direction(Direction.BUY) == ts.get_buy_price()
    assert ts.get_price_by_direction(Direction.SELL) == ts.get_sell_price()

    ts.buy(AssetPair(Asset("USDN"), Asset("WAVES")), 1, 10)
    ts.buy(AssetPair(Asset("USDN"), Asset("WAVES")), 1, 10)
    ts.update()

    signals = ts.get_trading_signals()
    assert len(ts.get_trading_signals()) == 0
    assert len(signals) >= 2
    assert any(x.name == 'filled_order' for x in signals)
