import pytest

from trading_system.risk_checker import RiskChecker
from trading import Order, Asset, AssetPair, Direction

from tests.logger.empty_logger_mock import empty_logger_mock
from tests.trading_interface.trading_interface_mock import TradingInterfaceMock


@pytest.fixture
def risk_checker(empty_logger_mock: empty_logger_mock) -> RiskChecker:
    return RiskChecker(
        trading_interface=TradingInterfaceMock.from_price_values([10]),
        config={
            "max_order_amount": 50,
            "max_order_price": 100,
            "available_assets": ["WAVES", "USDN", "USDT"],
            "max_order_count_per_period": 4,
            "rejection_period": "1m"
        })


@pytest.fixture
def order() -> Order:
    return Order(
        order_id=42,
        asset_pair=AssetPair(Asset("WAVES"), Asset("USDN")),
        amount=25,
        price=10,
        direction=Direction.BUY
    )


def test_big_order_amount(risk_checker: RiskChecker, order: Order) -> None:
    assert risk_checker.check(order)

    order.amount = 55
    assert not risk_checker.check(order)


def test_forbidden_asset(risk_checker: RiskChecker, order: Order) -> None:
    assert risk_checker.check(order)

    order.asset_pair = AssetPair(Asset("BTC"), Asset("USDN"))
    assert not risk_checker.check(order)

    order.asset_pair = AssetPair(Asset("WAVES"), Asset("BTC"))
    assert not risk_checker.check(order)


def test_big_order_price(risk_checker: RiskChecker, order: Order) -> None:
    assert risk_checker.check(order)

    order.price = 777
    assert not risk_checker.check(order)


def test_many_orders_per_period(risk_checker: RiskChecker, order: Order) -> None:
    for _ in range(4):
        assert risk_checker.check(order)

    for _ in range(4):
        assert not risk_checker.check(order)
