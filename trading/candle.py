class Candle:
    def __init__(self, ts: int, open_price: float, close_price: float,
                 low_price: float, high_price: float, volume: float):
        self.ts = ts
        self.open = open_price
        self.close = close_price
        self.low = low_price
        self.high = high_price
        self.volume = volume

    def get_lower_price(self) -> float:
        return min(self.open, self.close)

    def get_upper_price(self) -> float:
        return max(self.open, self.close)

    def get_mid_price(self) -> float:
        return (self.open + self.close) / 2

    def get_delta(self) -> float:
        return self.close - self.open

    def __repr__(self) -> str:
        return f"Timestamp: {self.ts} " \
               f"Open: {self.open} " \
               f"Close: {self.close} " \
               f"Low: {self.low} " \
               f"High: {self.high} " \
               f"Volume: {self.volume}"

    def __hash__(self):
        return hash((self.ts, self.open, self.close, self.low, self.high, self.volume))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Candle):
            return (self.ts, self.open, self.close, self.low, self.high, self.volume) \
                   == (other.ts, other.open, other.close, other.low, other.high, other.volume)
        return False
