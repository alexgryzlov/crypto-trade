import pytest
from mock import MagicMock

from tests.logger.empty_logger_mock import empty_logger_mock

from tests.trading_interface.trading_interface_mock import TradingInterfaceMock
from trading import Order, AssetPair, Asset, Direction
from trading_system.trading_system import OrdersHandler, CandlesHandler
import typing as tp

one_values = [1] * 10
ones_ti = TradingInterfaceMock.from_price_values(one_values)
ones_ti.order_is_filled = MagicMock(return_value=True)


@pytest.fixture(scope="module")
def sample_orders() -> tp.List[Order]:
    return [Order(i, AssetPair(Asset('WAVES'), Asset('USDN')), 1, 1, Direction.BUY) for i in range(10)]


@pytest.fixture
def orders_handler(request, sample_orders, empty_logger_mock) -> OrdersHandler:
    handler = OrdersHandler(request.param)
    for order in sample_orders:
        handler.add_new_order(order)
    return handler


@pytest.mark.parametrize("orders_handler", [ones_ti], indirect=True)
def test_active_orders_copy(sample_orders, orders_handler, empty_logger_mock):
    active_orders = orders_handler.get_active_orders()
    new_order = Order(1000, AssetPair(Asset('WAVES'), Asset('USDN')), 1, 1, Direction.BUY)
    active_orders.add(new_order)
    assert len(active_orders) != len(orders_handler.get_active_orders())


@pytest.mark.parametrize("orders_handler", [ones_ti], indirect=True)
def test_filled_orders(sample_orders, orders_handler, empty_logger_mock):
    assert len(orders_handler.get_active_orders()) == len(sample_orders)
    orders_handler.update()
    assert len(orders_handler.get_active_orders()) == 0
    assert len(orders_handler.get_new_filled_orders()) == len(sample_orders)
    assert len(orders_handler.get_new_filled_orders()) == 0


@pytest.mark.parametrize("orders_handler", [ones_ti], indirect=True)
def test_cancel_order(sample_orders, orders_handler, empty_logger_mock):
    assert len(orders_handler.get_active_orders()) == len(sample_orders)

    left = len(sample_orders)
    for order in sample_orders:
        orders_handler.cancel_order(order)
        left -= 1
        assert len(orders_handler.get_active_orders()) == left

    for order in sample_orders:
        orders_handler.add_new_order(order)

    assert len(orders_handler.get_active_orders()) == len(sample_orders)
    orders_handler.cancel_all()
    assert len(orders_handler.get_active_orders()) == 0


@pytest.mark.parametrize('ti', [ones_ti])
def test_candles_handler(ti: TradingInterfaceMock, empty_logger_mock):
    candles_handler = CandlesHandler(ti)
    while ti.update():
        assert candles_handler.received_new_candle()
        candles_handler.update()
        assert candles_handler.get_last_candle_timestamp() == ti.get_timestamp() - 1
    ti.refresh()
    assert candles_handler.received_new_candle() is False
    for i in range(5):
        ti.update()

    assert candles_handler.received_new_candle() is True
    candles_handler.update()
    assert candles_handler.get_last_candle_timestamp() == ti.get_timestamp() - 1
