import pytest
import typing as tp

from trading_system.risk_checker import RiskChecker
from trading_interface.trading_interface import TradingInterface
from trading import Asset, AssetPair, Direction

from tests.logger.empty_logger_mock import empty_logger_mock
from tests.trading_interface.trading_interface_mock import TradingInterfaceMock

trading_interface = TradingInterfaceMock.from_price_values([10, 11, 12])


@pytest.fixture
def risk_checker(request, empty_logger_mock: empty_logger_mock) -> RiskChecker:
    return RiskChecker(
        trading_interface=request.param,
        config={
            'max_order_amount': 50,
            'max_order_price': 100,
            'available_assets': ['WAVES', 'USDN', 'USDT'],
            'max_order_count_per_period': 4,
            'rejection_period': '2s'
        })


@pytest.fixture
def check_args() -> tp.Dict[str, tp.Any]:
    return {
        'asset_pair': AssetPair(Asset('WAVES'), Asset('USDN')),
        'amount': 25,
        'price': 10,
        'direction': Direction.BUY,
        'wallet': {
            Asset('WAVES'): 500,
            Asset('USDN'): 500
        }
    }


@pytest.mark.parametrize('risk_checker', [trading_interface], indirect=True)
def test_not_enough_assets(risk_checker: RiskChecker, check_args: tp.Dict[str, tp.Any]) -> None:
    assert risk_checker.check_order(**check_args)

    check_args['wallet'][Asset('WAVES')] = 0
    check_args['wallet'][Asset('USDN')] = 0
    assert not risk_checker.check_order(**check_args)


@pytest.mark.parametrize('risk_checker', [trading_interface], indirect=True)
def test_big_order_amount(risk_checker: RiskChecker, check_args: tp.Dict[str, tp.Any]) -> None:
    assert risk_checker.check_order(**check_args)

    check_args['amount'] = 55
    assert not risk_checker.check_order(**check_args)


@pytest.mark.parametrize('risk_checker', [trading_interface], indirect=True)
def test_forbidden_asset(risk_checker: RiskChecker, check_args: tp.Dict[str, tp.Any]) -> None:
    assert risk_checker.check_order(**check_args)

    check_args['asset_pair'] = AssetPair(Asset('BTC'), Asset('USDN'))
    assert not risk_checker.check_order(**check_args)

    check_args['asset_pair'] = AssetPair(Asset('WAVES'), Asset('BTC'))
    assert not risk_checker.check_order(**check_args)


@pytest.mark.parametrize('risk_checker', [trading_interface], indirect=True)
def test_big_order_price(risk_checker: RiskChecker, check_args: tp.Dict[str, tp.Any]) -> None:
    assert risk_checker.check_order(**check_args)

    check_args['price'] = 777
    assert not risk_checker.check_order(**check_args)


@pytest.mark.parametrize('risk_checker', [trading_interface], indirect=True)
def test_many_orders_per_period(risk_checker: RiskChecker, check_args: tp.Dict[str, tp.Any]) -> None:
    for _ in range(4):
        assert risk_checker.check_order(**check_args)

    for _ in range(4):
        assert not risk_checker.check_order(**check_args)

    for _ in range(2):
        trading_interface.update()

    assert risk_checker.check_order(**check_args)
