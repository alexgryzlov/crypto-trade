from strategy_runner.strategy_runner import StrategyRunner
from trading import AssetPair, Asset, Timeframe, TimeRange

from tests.strategies.dummy_strategy import DummyStrategy


def test_dummy_strategy_run():
    StrategyRunner().run_strategy(
        strategy=DummyStrategy,
        asset_pair=AssetPair(Asset('WAVES'), Asset('USDN')),
        timeframe=Timeframe('5m'),
        time_range=TimeRange.from_iso_format(
            from_ts='2021-02-10 00:00:00',
            to_ts='2021-02-10 12:00:00'))


def test_dummy_multiple_strategy_run():
    StrategyRunner().do_strategy_multiple_run(
        strategy=DummyStrategy,
        asset_pair=AssetPair(Asset('USDN'), Asset('WAVES')),
        timeframe=Timeframe('15m'),
        time_range=TimeRange.from_iso_format(
            from_ts='2021-02-10 00:00:00',
            to_ts='2021-02-11 00:00:00'),
        runs=4,
        processes=2)
