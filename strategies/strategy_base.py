from trading import Trend, TrendType


class StrategyBase:
    def handle_new_trend_signal(self, trend: Trend):
        pass

    def handle_extremum_signal(self, trend: TrendType):
        pass

    def handle_moving_average_signal(self, trend: TrendType):
        pass

    def handle_filled_order_signal(self, order):
        pass
