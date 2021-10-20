import importlib
import multiprocessing as mp
import traceback as tb
import typing as tp
from pathlib import Path
from time import sleep, time
from os import getpid

from helpers.typing.common_types import Config, ConfigsScope
from logger.logger import Logger
from base.config_parser import ConfigParser

from trading_interface.trading_interface import TradingInterface
from trading_interface.simulator.simulator import Simulator
from trading_interface.waves_exchange.waves_exchange_interface import WAVESExchangeInterface

from trading_system.trading_system import TradingSystem
from trading_system.trading_statistics import TradingStatistics

from trading_signal_detectors.trading_signal_detector import TradingSignalDetector
from trading_signal_detectors.extremum.extremum_signal_detector \
    import ExtremumSignalDetector
from trading_signal_detectors.moving_average.moving_average_signal_detector \
    import MovingAverageSignalDetector

from strategies.strategy_base import StrategyBase

from logger.logger import Logger

from trading import Timestamp, TimeRange, Signal


class StrategyRunner:
    def __init__(self,
                 base_config: ConfigsScope,
                 simulator_config: Config,
                 exchange_config: Config):
        self.base_config = base_config
        self.simulator_config = simulator_config
        self.exchange_config = exchange_config
        self.logger = Logger(f"Runner{getpid()}",
                             config=self.base_config['strategy_runner']['logger'])
        self._ti: tp.Optional[TradingInterface] = None
        self._ts: tp.Optional[TradingSystem] = None
        self._strategy_inst: tp.Optional[StrategyBase] = None
        self._signal_detectors: tp.List[TradingSignalDetector] = []
        self._stdout_frequency = self.base_config['strategy_runner']['stdout_frequency']
        self._between_iteration_pause = self.base_config['strategy_runner']['between_iteration_pause']

    def _get_strategy_instance(self) -> tp.Any:
        module_path = 'strategies' + ('.' + self.base_config["strategy"]["dir"]) * 2
        module = importlib.import_module(module_path)
        strategy_class = module.__getattribute__(self.base_config["strategy"]["name"])
        path = 'strategies/' + self.base_config["strategy"]["dir"] + '/config.json'
        config = ConfigParser.load_config(Path(path))
        strategy_instance = strategy_class(config=config)
        return strategy_instance

    def run_simulation(
            self,
            time_range: TimeRange,
            logs_path: tp.Optional[Path] = None,
            pretty_print: bool = True) -> TradingStatistics:

        def get_progress() -> float:
            return (min(self._ti.get_timestamp(), time_range.to_ts) - time_range.from_ts)\
                   / time_range.get_range() * 100

        Logger.set_log_file_name(Timestamp.to_iso_format(time_range.from_ts))
        if logs_path is not None:
            Logger.set_logs_path(logs_path)

        self._ti = Simulator(
            time_range=time_range,
            trading_config=self.base_config['trading_interface'],
            exchange_config=self.simulator_config
        )
        Logger.set_clock(self._ti.get_clock())

        self._init_trading()

        last_checkpoint = 0
        self.logger.info("Simulation started")
        while self._ti.is_alive():
            current_checkpoint = get_progress() // self._stdout_frequency * self._stdout_frequency
            if current_checkpoint != last_checkpoint:
                last_checkpoint = current_checkpoint
                self.logger.info(f"{last_checkpoint}% of simulation passed."
                                 f" Simulation time: {Timestamp.to_iso_format(self._ti.get_timestamp())}")

            self._do_trading_iteration()

        return self._stop_trading(pretty_print)

    def run_simulation_on_periods(
            self,
            time_range: TimeRange,
            period: tp.Optional[int] = None,
            runs: tp.Optional[int] = None,
            visualize: bool = False,
            processes: int = 4,
            logs_path: tp.Optional[Path] = None,
            pretty_print: bool = True) -> TradingStatistics:

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
                self.run_simulation,
                kwds={
                    'time_range': TimeRange(current_ts, next_ts),
                    'logs_path': logs_path},
                callback=lambda run_result: run_results.append(run_result),
                error_callback=lambda e: tb.print_exception(type(e), e, None))
            current_ts = next_ts

        pool.close()
        pool.join()
        stats = TradingStatistics.merge(run_results)
        if pretty_print:
            stats.pretty_print()
        else:
            print(stats)

        if visualize:
            TradingStatistics.visualize(run_results)

        return stats

    def run_exchange(
            self,
            logs_path: tp.Optional[Path] = None,
            pretty_print: bool = True) -> TradingStatistics:

        # TODO: don't use time()
        Logger.set_log_file_name(Timestamp.to_iso_format(int(time())))
        if logs_path is not None:
            Logger.set_logs_path(logs_path)

        self._ti = WAVESExchangeInterface(
            trading_config=self.base_config['trading_interface'],
            exchange_config=self.exchange_config)
        Logger.set_clock(self._ti.get_clock())

        self._init_trading()

        while self._ti.is_alive():
            self._do_trading_iteration()
            sleep(self._between_iteration_pause)

        return self._stop_trading(pretty_print)

    def _init_trading(self) -> None:
        self._ts = TradingSystem(
            trading_interface=self._ti,
            config=self.base_config['trading_system'])

        self._strategy_inst = self._get_strategy_instance()
        self._strategy_inst.init_trading(self._ts)
        self._signal_detectors = self._strategy_inst.get_signal_detectors()
        self._signal_detectors.append(self._ts)

    def _do_trading_iteration(self) -> None:
        self._ts.update()
        signals: tp.List[Signal] = []
        for detector in self._signal_detectors:
            signals += detector.get_trading_signals()
        for signal in signals:
            self._strategy_inst.__getattribute__(
                f'handle_{signal.name}_signal')(signal.content)
        self._strategy_inst.update()

    def _stop_trading(self, pretty_print: bool) -> TradingStatistics:
        self._ts.stop_trading()
        self._ti.stop_trading()
        self._ts.update()

        stats = self._ts.get_trading_statistics()
        Logger.store_log()
        if pretty_print:
            stats.pretty_print()
        else:
            print(stats)

        return stats
