from pathlib import Path

from market_data_api.market_data_downloader import MarketDataDownloader
from base.config_parser import ConfigParser

from strategy_runner.strategy_runner import StrategyRunner
from strategies.trend_strategy.trend_strategy import TrendStrategy

from trading import TimeRange

from trading_interface.waves_exchange.waves_exchange_interface import WAVESExchangeInterface

if __name__ == "__main__":
    base_config = ConfigParser.load_config(Path('configs/base.json'))

    MarketDataDownloader.init(base_config['market_data_downloader'])

    strategy_runner = StrategyRunner(
        base_config=base_config,
        simulator_config=ConfigParser.load_config(Path('configs/simulator.json')),
        exchange_config=ConfigParser.load_config(Path('configs/waves.json')))

    e = WAVESExchangeInterface(base_config['trading_interface'])
    print(e.get_sell_price())
   # print(e.get_buy_price(), e.get_sell_price())

    # strategy_runner.run_simulation_on_periods(
    #    strategy=TrendStrategy,
    #    strategy_config={},
    #    time_range=TimeRange.from_iso_format(
    #        from_ts='2021-02-01 00:00:00',
    #        to_ts='2021-02-01 12:00:00'),
    #    runs=4,
    #    processes=2,
    #    visualize=False)
