import pytest
import mock

from tests.logger.empty_logger_mock import empty_logger_mock

from tests.trading_interface.trading_interface_mock import TradingInterfaceMock
from trading import Order, AssetPair, Asset, Direction
from trading_system.trading_system import TradingSystem, OrdersHandler, CandlesHandler
import typing as tp

one_values = [1] * 10
ones_ti = TradingInterfaceMock.from_price_values(one_values)


@pytest.mark.parametrize('ti', [ones_ti])
def test_orders_handler(ti: TradingInterfaceMock, empty_logger_mock):
    orders = [Order(i, AssetPair(Asset('WAVES'), Asset('USDN')), 1, 1, Direction.BUY) for i in range(10)]

    def always_true(order: Order) -> bool:
        return True

    with mock.patch.object(ti, 'order_is_filled', new=always_true):
        orders_handler = OrdersHandler(ti)
        for order in orders:
            orders_handler.add_new_order(order)

        active_orders = orders_handler.get_active_orders()
        new_order = Order(1000, AssetPair(Asset('WAVES'), Asset('USDN')), 1, 1, Direction.BUY)
        active_orders.add(new_order)
        assert len(active_orders) != len(orders_handler.get_active_orders())

        assert len(orders_handler.get_active_orders()) == len(orders)
        orders_handler.update()
        assert len(orders_handler.get_active_orders()) == 0
        assert len(orders_handler.get_new_filled_orders()) == len(orders)
        assert len(orders_handler.get_new_filled_orders()) == 0

        for order in orders:
            orders_handler.add_new_order(order)

        assert len(orders_handler.get_active_orders()) == len(orders)

        left = len(orders)
        for order in orders:
            orders_handler.cancel_order(order)
            left -= 1
            assert len(orders_handler.get_active_orders()) == left

        for order in orders:
            orders_handler.add_new_order(order)

        assert len(orders_handler.get_active_orders()) == len(orders)
        orders_handler.cancel_all()
        assert len(orders_handler.get_active_orders()) == 0


@pytest.mark.parametrize('ti', [ones_ti])
def test_candles_handler(ti: TradingInterfaceMock, empty_logger_mock):
    candles_handler = CandlesHandler(ti)
    time = 0
    while ti.update():
        assert candles_handler.received_new_candle()
        candles_handler.update()
        assert candles_handler.get_last_candle_timestamp() == time
        time += 1
    ti.refresh()
    assert candles_handler.received_new_candle() == False
    for i in range(5):
        ti.update()

    assert candles_handler.received_new_candle() == True
    candles_handler.update()
    assert candles_handler.get_last_candle_timestamp() == ti.get_timestamp() - 1
