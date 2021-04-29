import importlib
import multiprocessing as mp
import traceback as tb
import typing as tp
from pathlib import Path

from helpers.typing.common_types import Config, ConfigsScope
from logger.logger import Logger
from base.config_parser import ConfigParser

from trading_interface.simulator.simulator import Simulator
from strategies.strategy_base import StrategyBase
from trading_system.trading_system import TradingSystem
from trading_system.trading_statistics import TradingStatistics

from trading import Timestamp, TimeRange

from trading_signal_detectors import (
    ExtremumSignalDetector,
    MovingAverageSignalDetector,
    ExpMovingAverageSignalDetector,
    StochasticRSISignalDetector
)


class StrategyRunner:
    def __init__(self, base_config: ConfigsScope):
        self.base_config = base_config

    def _get_strategy_instance(self) -> tp.Any:
        module = importlib.import_module(self.base_config["strategy"]["strategy_module"])
        strategy_class = module.__getattribute__(self.base_config["strategy"]["strategy_name"])
        config = {}
        if "path_to_config" in self.base_config["strategy"]:
            config = ConfigParser.load_config(
                Path(self.base_config["strategy"]["path_to_config"]))
        strategy_instance = strategy_class(config=config)
        return strategy_instance

    def run_strategy(
            self,
            time_range: TimeRange,
            logs_path: tp.Optional[Path] = None) -> TradingStatistics:

        Logger.set_log_file_name(Timestamp.to_iso_format(time_range.from_ts))
        if logs_path is not None:
            Logger.set_logs_path(logs_path)

        simulator = Simulator(
            time_range=time_range,
            config=self.base_config['trading_interface'])
        Logger.set_clock(simulator.get_clock())

        trading_system = TradingSystem(
            trading_interface=simulator,
            config=self.base_config['trading_system'])

        strategy_instance = self._get_strategy_instance()
        strategy_instance.init_trading(trading_system)
        signal_detectors = strategy_instance.get_signal_detectors()
        signal_detectors.append(trading_system)

        while simulator.is_alive():
            trading_system.update()
            signals = []
            for detector in signal_detectors:
                signals += detector.get_trading_signals()
            for signal in signals:
                strategy_instance.__getattribute__(
                    f'handle_{signal.name}_signal')(signal.content)
            strategy_instance.update()

        trading_system.stop_trading()
        simulator.stop_trading()
        trading_system.update()

        stats = trading_system.get_trading_statistics()
        Logger.store_log()
        print(stats)

        return stats

    def run_strategy_on_periods(
            self,
            time_range: TimeRange,
            period: tp.Optional[int] = None,
            runs: tp.Optional[int] = None,
            visualize: bool = False,
            processes: int = 4,
            logs_path: tp.Optional[Path] = None) -> TradingStatistics:

        if period is None and runs is None:
            raise ValueError('Run type not selected')

        period = period if period is not None else \
            time_range.get_range() // runs  # type: ignore
        runs = runs if runs is not None else \
            time_range.get_range() // period

        pool = mp.Pool(processes=processes, maxtasksperchild=1)
        current_ts = time_range.from_ts
        run_results: tp.List[TradingStatistics] = []

        for run_id in range(runs):
            next_ts = current_ts + period
            pool.apply_async(
                self.run_strategy,
                kwds={
                    'time_range': TimeRange(current_ts, next_ts),
                    'logs_path': logs_path},
                callback=lambda run_result: run_results.append(run_result),
                error_callback=lambda e: tb.print_exception(type(e), e, None))
            current_ts = next_ts

        pool.close()
        pool.join()
        stats = TradingStatistics.merge(run_results)
        print(stats)

        if visualize:
            TradingStatistics.visualize(run_results)

        return stats
