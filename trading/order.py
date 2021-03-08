from enum import IntEnum

from trading import AssetPair


class Direction(IntEnum):
    BUY = -1
    SELL = 1


class Order:
    def __init__(self, order_id: int, asset_pair: AssetPair, amount: int, price: float, direction: Direction):
        self.order_id = order_id
        self.asset_pair = asset_pair
        self.amount = amount
        self.price = price
        self.direction = direction

    def __repr__(self):
        return f"Order{self.order_id}"

    def __str__(self):
        return f"OrderId: {self.order_id} " \
               f"AssetPair: {self.asset_pair.main_asset}-{self.asset_pair.secondary_asset} " \
               f"Amount: {self.amount} " \
               f"Price: {self.price} " \
               f"Direction: {self.direction}"
