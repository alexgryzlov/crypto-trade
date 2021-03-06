import ccxt

from trading.candle import Candle
from trading.asset import AssetPair

CANDLES_PER_REQUEST = 1440


class MarketDataDownloader:
    def __init__(self):
        self.exchange = ccxt.wavesexchange()

    def get_candles(self, asset_pair: AssetPair, timeframe: str, from_ts, to_ts):
        candles = []
        current_ts = from_ts

        while current_ts <= to_ts:
            new_candles = self.exchange.fetch_ohlcv(
                symbol=str(asset_pair),
                timeframe=timeframe,
                since=self.__to_milliseconds(current_ts),
                limit=CANDLES_PER_REQUEST)

            for candle_data in new_candles:
                new_candle = Candle(
                    ts=self.__from_milliseconds(candle_data[0]),
                    open=candle_data[1],
                    close=candle_data[2],
                    low=candle_data[3],
                    high=candle_data[4],
                    volume=candle_data[5])
                if new_candle.ts > to_ts:
                    break
                candles.append(new_candle)

            if not len(candles):
                break
            current_ts = candles[-1].ts + 1

        return candles

    @staticmethod
    def __to_milliseconds(ts):
        return ts * 1000

    @staticmethod
    def __from_milliseconds(ts):
        return ts // 1000
