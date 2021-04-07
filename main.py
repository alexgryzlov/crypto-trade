from pathlib import Path

from market_data_api.market_data_downloader import MarketDataDownloader
from base.config_parser import ConfigParser

from strategy_runner.strategy_runner import StrategyRunner
from strategies.trend_strategy.trend_strategy import TrendStrategy

from trading import TimeRange

if __name__ == "__main__":
    base_config = ConfigParser.load_config(Path('configs/base.json'))

    MarketDataDownloader.init(base_config['market_data_downloader'])

    strategy_runner = StrategyRunner(
        base_config=base_config)

    strategy_runner.run_strategy_on_periods(
        strategy=TrendStrategy,
        strategy_config={},
        time_range=TimeRange.from_iso_format(
            from_ts='2021-02-01 00:00:00',
            to_ts='2021-02-01 12:00:00'),
        runs=4,
        processes=2,
        visualize=False)
