from trading_interface.simulator.clock_simulator import ClockSimulator
from trading_interface.simulator.simulator import Simulator
from trading_system.trading_system import TradingSystem

from trading_signal_detectors.extremum.extremum_signal_detector \
    import ExtremumSignalDetector
from trading_signal_detectors.moving_average.moving_average_signal_detector \
    import MovingAverageSignalDetector

from strategies.strategy_base import StrategyBase

from logger.object_log import ObjectLog
from logger.logger import Logger

from trading import AssetPair, Timeframe

from pathlib import Path
import typing as tp
import json


class StrategyRunner:
    def __init__(self) -> None:
        pass

    def run_strategy(
            self, strategy: tp.Type[StrategyBase], asset_pair: AssetPair,
            timeframe: Timeframe, from_ts: int, to_ts: int,
            path_to_config: tp.Optional[Path] = None) -> None:
        clock = ClockSimulator(from_ts, timeframe, candles_lifetime=15)
        trading_interface = Simulator(asset_pair=asset_pair,
                                      from_ts=from_ts,
                                      to_ts=to_ts,
                                      clock=clock)
        Logger.set_clock(clock)
        trading_system = TradingSystem(trading_interface)
        signal_detectors = [
            ExtremumSignalDetector(trading_system, 2),
            MovingAverageSignalDetector(trading_system, 25, 50)]

        try:
            config = json.load(open(path_to_config, 'r'))  # type: ignore
        except:
            config = {}
        strategy_inst = strategy(trading_system=trading_system,
                                 asset_pair=asset_pair,
                                 **config)

        while trading_interface.is_alive():
            trading_system.update()
            signals = []
            for detector in signal_detectors:
                signals += detector.get_trading_signals()
            for signal in signals:
                strategy_inst.__getattribute__(
                    f'handle_{signal.name}_signal')(signal.content)
            strategy_inst.update()

        print(trading_system.get_balance())
        print(trading_system.get_active_orders())
        print(trading_system.get_wallet())

        ObjectLog().store_log()
