from trading_system.trading_system_handler import TradingSystemHandler
from trading_interface.trading_interface import TradingInterface
from logger.log_events import TrendLinesEvent
from logger.logger import Logger
from trading.trend import TrendLine
import base.geometry.convex_hull as geom

import numpy as np

MIN_CANDLE_COUNT = 5
MAX_LAST_CANDLE_COUNT = 40
PRICE_SHIFT = 0.13


class TrendHandler(TradingSystemHandler):
    def __init__(self, trading_interface: TradingInterface):
        super().__init__(trading_interface)
        self.ti = trading_interface
        self.logger = Logger("TrendHandler")

    def update(self):
        if not super().received_new_candle():
            return
        lower_trend_line, upper_trend_line = self.get_trend_lines()
        self.logger.trading(TrendLinesEvent(lower_trend_line, upper_trend_line))

    def get_trend_lines(self):  # -> Tuple[TrendLine, TrendLine]:
        candles = self.ti.get_last_n_candles(MAX_LAST_CANDLE_COUNT)

        if len(candles) < MIN_CANDLE_COUNT:
            return None, None

        ts_offset = candles[0].ts
        max_price = max([candle.get_upper_price() for candle in candles])
        coef = max_price / (candles[1].ts - candles[0].ts) / 20

        lower_bound = np.array(
            [((candles[index].ts - ts_offset) * coef, candles[index].get_lower_price()) for index in
             range(len(candles))])

        upper_bound = np.array(
            [((candles[index].ts - ts_offset) * coef, candles[index].get_upper_price()) for index in
             range(len(candles))])

        lower_trend_line = self.__calculate_trend_line(lower_bound, geom.get_lower_bound)
        upper_trend_line = self.__calculate_trend_line(upper_bound, geom.get_upper_bound)

        if lower_trend_line is not None:
            lower_trend_line.k *= coef
            lower_trend_line.b -= lower_trend_line.k * ts_offset
            lower_trend_line.b -= PRICE_SHIFT

        if upper_trend_line is not None:
            upper_trend_line.k *= coef
            upper_trend_line.b -= upper_trend_line.k * ts_offset
            upper_trend_line.b += PRICE_SHIFT

        return lower_trend_line, upper_trend_line

    def __calculate_trend_line(self, points, calc_convex_bound):
        BOUND = 0.005
        for iter in range(10):
            best_line = None
            convex_bound = calc_convex_bound(points[-MIN_CANDLE_COUNT:], is_sorted=True)
            for point_count in range(MIN_CANDLE_COUNT + 1, len(points) + 1):
                convex_bound = calc_convex_bound(
                    np.concatenate([[points[len(points) - point_count]], convex_bound]), is_sorted=True)
                line = geom.put_line(convex_bound)
                if self.__calculate_penalty(convex_bound, TrendLine(*line)) < BOUND:
                    best_line = line
            if best_line is None:
                BOUND *= 2
            else:
                return TrendLine(*best_line)
        return None

    def __calculate_penalty(self, points, line: TrendLine):
        penalty = 0.0
        for p in points:
            penalty += (p[1] - line.get_value_at(p[0])) ** 2
        return penalty
