class Candle:
    def __init__(self, ts, open, close, low, high):
        self.ts = ts
        self.open = open
        self.close = close
        self.low = low
        self.high = high

    def get_lower_price(self):
        return min(self.open, self.close)

    def get_upper_price(self):
        return max(self.open, self.close)

    def get_mid_price(self):
        return (self.open + self.close) / 2

    def get_delta(self):
        return self.close - self.open

    def __repr__(self):
        return f"Timestamp: {self.ts} " \
               f"Open: {self.open} " \
               f"Close: {self.close} " \
               f"Low: {self.low} " \
               f"High: {self.high}"
