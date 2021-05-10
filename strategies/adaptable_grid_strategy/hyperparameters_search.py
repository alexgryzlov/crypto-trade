import json
import typing as tp
from itertools import product
from pathlib import Path

from base.config_parser import ConfigParser
from market_data_api.market_data_downloader import MarketDataDownloader
from strategy_runner.strategy_runner import StrategyRunner
from trading import TimeRange
from trading_system.trading_statistics import TradingStatistics


def generate_config(config: tp.Dict[str, tp.Any]) -> None:
    with open('strategies/adaptable_grid_strategy/config.json', 'w') as f:
        json.dump(config, f)


def grid_generator(
        grid: tp.Dict[str, tp.List[tp.Any]]
        ) -> tp.Generator[tp.Dict[str, tp.Any], None, None]:
    names = list(grid.keys())
    param_grid = product(*list(grid.values()))
    for params in param_grid:
        yield dict(zip(names, params))


time_range = TimeRange.from_iso_format(
    from_ts='2021-01-01 00:00:00',
    to_ts='2021-05-01 00:00:00')
base_config = ConfigParser.load_config(Path('configs/base.json'))
MarketDataDownloader.init(base_config['market_data_downloader'])
strategy_runner = StrategyRunner(base_config=base_config)

param_grid: tp.Dict[str, tp.List[tp.Any]] = {
  'asset_pair': [['USDT', 'USDN']],
  'threshold': [0.4],
  'window': [80],
  'coef': [25],
  'candles_timeout': [48],
  'candles_lifetime': [8],
  'timeout_only': [True, False],
  'handle_filled_orders': [False]
}
best_profit = float('-inf')
best_stats: tp.Optional[TradingStatistics] = None
best_params: tp.Dict[str, tp.List[tp.Any]] = {}

for params_dict in grid_generator(param_grid):
    generate_config(params_dict)
    stats = strategy_runner.run_strategy(time_range=time_range)
    profit = stats.calc_relative_delta()
    if profit > best_profit:
        best_profit = profit
        best_stats = stats
        best_params = params_dict


print(f'Optimal parameters: {best_params}')
print(f'Profit: {best_profit}%')
