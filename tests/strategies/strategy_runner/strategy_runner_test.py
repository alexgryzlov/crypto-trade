import pytest

from helpers.typing.common_types import Config, ConfigsScope

from strategies.strategy_runner.strategy_runner import StrategyRunner
from trading import TimeRange

from tests.logger.empty_logger_mock import empty_logger_mock
from tests.market_data_api.md_downloader import market_data_downloader


@pytest.fixture
def strategy_runner(
        base_config: ConfigsScope,
        simulator_config: Config,
        market_data_downloader: market_data_downloader) -> StrategyRunner:
    return StrategyRunner(
        base_config=base_config,
        simulator_config=simulator_config,
        exchange_config={}
    )


def test_dummy_simulation_run(
        strategy_runner: StrategyRunner,
        empty_logger_mock: empty_logger_mock) -> None:
    strategy_runner.run_simulation(
        time_range=TimeRange.from_iso_format(
            from_ts='2021-02-10 00:00:00',
            to_ts='2021-02-10 12:00:00'))


def test_dummy_multiple_simulation_run(
        strategy_runner: StrategyRunner,
        empty_logger_mock: empty_logger_mock) -> None:
    strategy_runner.run_simulation_on_periods(
        time_range=TimeRange.from_iso_format(
            from_ts='2021-02-10 00:00:00',
            to_ts='2021-02-11 00:00:00'),
        runs=4,
        processes=2,
        visualize=False)
