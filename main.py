from strategy_runner.strategy_runner import StrategyRunner
from strategies.trend_strategy.trend_strategy import TrendStrategy

from trading import AssetPair, Asset, Timeframe, TimeRange

if __name__ == "__main__":
    StrategyRunner().run_strategy_on_periods(
        strategy=TrendStrategy,
        strategy_config={},
        asset_pair=AssetPair(Asset('WAVES'), Asset('USDN')),
        timeframe=Timeframe('5m'),
        time_range=TimeRange.from_iso_format(
            from_ts='2021-02-01 00:00:00',
            to_ts='2021-02-01 12:00:00'),
        runs=4,
        processes=2,
        visualize=False)
