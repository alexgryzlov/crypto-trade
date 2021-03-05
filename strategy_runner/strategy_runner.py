from trading_interface.simulator.clock_simulator import ClockSimulator
from trading_interface.simulator.simulator import Simulator
from trading_system.trading_system import TradingSystem

from trading_signal_detectors.extremum.extremum_signal_detector import ExtremumSignalDetector
from trading_signal_detectors.moving_average.moving_average_signal_detector import MovingAverageSignalDetector

from logger.object_log import ObjectLog
from logger import logger

from trading.asset import AssetPair


class StrategyRunner:
    def __init__(self):
        pass

    def run_strategy(self, strategy, asset_pair: AssetPair, timeframe, from_ts, to_ts):
        clock = ClockSimulator(from_ts, timeframe, candles_lifetime=15)
        trading_interface = Simulator(asset_pair=asset_pair,
                                      from_ts=from_ts,
                                      to_ts=to_ts,
                                      clock=clock)
        logger.set_clock(clock)
        trading_system = TradingSystem(trading_interface)
        signal_detectors = [ExtremumSignalDetector(trading_system, 2),
                            MovingAverageSignalDetector(trading_system, 25, 50)]
        strategy = strategy(trading_system=trading_system,
                            asset_pair=asset_pair)

        while trading_interface.is_alive():
            trading_system.update()
            signals = []
            for detector in signal_detectors:
                signals += detector.get_trading_signals()
            for signal in signals:
                strategy.__getattribute__(f'handle_{signal.name}_signal')(signal.content)
            strategy.update()

        print(trading_system.get_balance())
        print(trading_system.get_active_orders())
        print(trading_system.get_wallet())

        ObjectLog().store_log()
