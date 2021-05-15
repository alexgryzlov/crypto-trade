from pathlib import Path

from market_data_api.market_data_downloader import MarketDataDownloader
from base.config_parser import ConfigParser

from strategy_runner.strategy_runner import StrategyRunner
from strategies.trend_strategy.trend_strategy import TrendStrategy
from strategies.grid_strategy.grid_strategy import GridStrategy

from trading import TimeRange

if __name__ == "__main__":
    base_config = ConfigParser.load_config(Path('configs/base.json'))

    MarketDataDownloader.init(base_config['market_data_downloader'])

    strategy_runner = StrategyRunner(
        base_config=base_config,
        simulator_config={},
        exchange_config=ConfigParser.load_config(Path('configs/waves.json'))['testnet']
    )

    strategy_runner.run_exchange(
        strategy=GridStrategy,
        strategy_config=ConfigParser.load_config(Path('strategies/grid_strategy/config.json'))
    )
