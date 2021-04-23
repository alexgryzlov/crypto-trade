from trading import AssetPair, TrendLine, Candle, Order
from varname import argname
import typing as tp


def _create_dict(*args: tp.Any) -> tp.Dict[str, tp.Any]:
    """
    Given arguments arg_1, ..., arg_n, return 
    dict {'arg_1': arg_1, ..., 'arg_n': arg_n} 
    """
    return dict(zip(argname(args), args))


class LogEvent:
    def __init__(self, msg: str, obj: tp.Any):
        self.msg = msg
        self.obj = obj


class TrendLinesEvent(LogEvent):
    def __init__(self,
                 lower_trend_line: TrendLine,
                 upper_trend_line: TrendLine):
        super().__init__('Trend lines updated',
                         _create_dict(lower_trend_line, upper_trend_line))


class CurveEvent(LogEvent):
    name = 'Custom Curve'

    def __init__(self,
                 msg: str,
                 value: float,
                 params: str):
        super().__init__(msg,
                         _create_dict(value, params))


class ExpMovingAverageEvent(CurveEvent):
    name = 'Exp Moving Average'

    def __init__(self, value: float, window_size: int):
        super().__init__(
            f'New EMA of last {window_size} elements {value}',
            value,
            f'{window_size}')


class MovingAverageEvent(CurveEvent):
    name = 'Moving Average'

    def __init__(self, average_value: float, window_size: int):
        super().__init__(
            f'New average of last {window_size} elements {average_value}',
            average_value,
            f'{window_size}',
        )


class BuyEvent(LogEvent):
    def __init__(self, asset_pair: AssetPair, amount: float,
                 price: float, order_id: int):
        super().__init__(
            f'Buying {amount} of {asset_pair.amount_asset} for {price} '
            f'{asset_pair.price_asset}, order {order_id}',
            _create_dict(asset_pair.amount_asset, asset_pair.price_asset,
                         amount, price,
                         order_id))


class SellEvent(LogEvent):
    def __init__(self, asset_pair: AssetPair, amount: float,
                 price: float, order_id: int) -> None:
        super().__init__(
            f'Selling {amount} of {asset_pair.price_asset} for {price} '
            f'{asset_pair.amount_asset}, order {order_id}',
            _create_dict(asset_pair.amount_asset, asset_pair.price_asset,
                         amount, price,
                         order_id))


class CancelEvent(LogEvent):
    def __init__(self, order: Order):
        super().__init__(f'Cancel order {order.order_id}',
                         {'amount_asset': order.asset_pair.amount_asset,
                          'price_asset': order.asset_pair.price_asset,
                          'amount': order.amount,
                          'price': order.price,
                          'order_id': order.order_id})


class FilledOrderEvent(LogEvent):
    def __init__(self, order_id: int) -> None:
        super().__init__(f'Order {order_id} is filled',
                         _create_dict(order_id))


class NewCandleEvent(LogEvent):
    def __init__(self, candle: Candle) -> None:
        super().__init__(f'New candle: {candle}',
                         _create_dict(candle))
