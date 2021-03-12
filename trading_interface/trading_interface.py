from trading import AssetPair, Order


class TradingInterface:
    def is_alive(self):
        pass

    def get_timestamp(self):
        pass

    def get_balance(self):
        pass

    def buy(self, asset_pair: AssetPair, amount: int, price: float):
        pass

    def sell(self, asset_pair: AssetPair, amount: int, price: float):
        pass

    def cancel_order(self, order: Order):
        pass

    def cancel_all(self):
        pass

    def order_is_filled(self, order: Order):
        pass

    def get_buy_price(self):
        pass

    def get_sell_price(self):
        pass

    def get_orderbook(self):
        pass

    def get_last_n_candles(self, n: int):
        pass
