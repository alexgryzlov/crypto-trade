import pytest
from pathlib import Path

from tests.configs import base_config
from helpers.typing.common_types import ConfigsScope

from strategy_runner.strategy_runner import StrategyRunner
from trading import TimeRange

from tests.logger.empty_logger_mock import empty_logger_mock


@pytest.fixture
def strategy_runner(base_config: ConfigsScope) -> StrategyRunner:
    return StrategyRunner(base_config=base_config)


def test_dummy_strategy_run(strategy_runner: StrategyRunner, empty_logger_mock: empty_logger_mock) -> None:
    strategy_runner.run_strategy(
        time_range=TimeRange.from_iso_format(
            from_ts='2021-02-10 00:00:00',
            to_ts='2021-02-10 12:00:00'))


def test_dummy_multiple_strategy_run(strategy_runner: StrategyRunner, empty_logger_mock: empty_logger_mock) -> None:
    strategy_runner.run_strategy_on_periods(
        time_range=TimeRange.from_iso_format(
            from_ts='2021-02-10 00:00:00',
            to_ts='2021-02-11 00:00:00'),
        runs=4,
        processes=2,
        visualize=False)
