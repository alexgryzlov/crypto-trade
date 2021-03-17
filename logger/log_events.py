from trading import Asset, TrendLine, Candle, Order
import typing as tp


class LogEvent:
    def __init__(self, msg: str, obj: tp.Any):
        self.msg = msg
        self.obj = obj


class TrendLinesEvent(LogEvent):
    def __init__(self,
                 lower_trend_line: TrendLine,
                 upper_trend_line: TrendLine):
        super().__init__('Trend lines updated',
                         {'lower_trend_line': lower_trend_line,
                          'upper_trend_line': upper_trend_line})


class MovingAverageEvent(LogEvent):
    def __init__(self, average_value: float, window_size: int):
        super().__init__(
            f'New average of last {window_size} elements {average_value}',
            {'average_value': average_value,
             'window_size': window_size})


class BuyEvent(LogEvent):
    def __init__(self, buy_asset: Asset, sell_asset: Asset, amount: int,
                 price: float, order_id: int):
        super().__init__(f'Buying {amount} of {buy_asset} for {price} '
                         f'{sell_asset}, order {order_id}',
                         {'buy_asset': buy_asset,
                          'sell_asset': sell_asset,
                          'amount': amount,
                          'price': price,
                          'order_id': order_id})


class SellEvent(LogEvent):
    def __init__(self, sell_asset: Asset, buy_asset: Asset, amount: int,
                 price: float, order_id: int) -> None:
        super().__init__(f'Selling {amount} of {sell_asset} for {price} '
                         f'{buy_asset}, order {order_id}',
                         {'buy_asset': buy_asset,
                          'sell_asset': sell_asset,
                          'amount': amount,
                          'price': price,
                          'order_id': order_id})


class CancelEvent(LogEvent):
    def __init__(self, order: Order):
        super().__init__(f'Cancel order {order.order_id}',
                         {'buy_asset': order.asset_pair.main_asset,
                          'sell_asset': order.asset_pair.secondary_asset,
                          'amount': order.amount,
                          'price': order.price,
                          'order_id': order.order_id})


class FilledOrderEvent(LogEvent):
    def __init__(self, order_id: int) -> None:
        super().__init__(f'Order {order_id} is filled',
                         {'order_id': order_id})


class NewCandleEvent(LogEvent):
    def __init__(self, candle: Candle) -> None:
        super().__init__(f'New candle: {candle}',
                         {'candle': candle})
