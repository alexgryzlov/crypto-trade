import pytest

from strategy_runner.strategy_runner import StrategyRunner
from trading import AssetPair, Asset, Timeframe, TimeRange

from tests.logger.empty_logger_mock import empty_logger_mock
from tests.strategies.strategy_mock import StrategyMock

from base.config_parser import ConfigParser


@pytest.fixture
def strategy_runner() -> StrategyRunner:
    return StrategyRunner(base_config=ConfigParser().load_config('configs/base.ini'))


def test_dummy_strategy_run(strategy_runner: StrategyRunner, empty_logger_mock: empty_logger_mock) -> None:
    strategy_runner.run_strategy(
        strategy=StrategyMock,
        strategy_config={},
        asset_pair=AssetPair(Asset('WAVES'), Asset('USDN')),
        timeframe=Timeframe('5m'),
        time_range=TimeRange.from_iso_format(
            from_ts='2021-02-10 00:00:00',
            to_ts='2021-02-10 12:00:00'))


def test_dummy_multiple_strategy_run(strategy_runner: StrategyRunner, empty_logger_mock: empty_logger_mock) -> None:
    strategy_runner.run_strategy_on_periods(
        strategy=StrategyMock,
        strategy_config={},
        asset_pair=AssetPair(Asset('USDT'), Asset('USDN')),
        timeframe=Timeframe('15m'),
        time_range=TimeRange.from_iso_format(
            from_ts='2021-02-10 00:00:00',
            to_ts='2021-02-11 00:00:00'),
        runs=4,
        processes=2,
        visualize=False)
