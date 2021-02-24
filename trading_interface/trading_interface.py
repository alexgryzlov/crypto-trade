class TradingInterface:
    def is_alive(self):
        pass

    def get_timestamp(self):
        pass

    def get_balance(self):
        pass

    def buy(self, asset_pair, amount, price):
        pass

    def sell(self, asset_pair, amount, price):
        pass

    def cancel_order(self, order):
        pass

    def order_is_filled(self, order):
        pass

    def get_buy_price(self):
        pass

    def get_sell_price(self):
        pass

    def get_orderbook(self):
        pass

    def get_last_n_candles(self, n):
        pass
