import requests
from trading.candle import Candle

MARKET_DATA_ADDRESS = "http://marketdata.wavesplatform.com"


class MarketDataDownloader:
    def __init__(self, asset_pair):
        self.asset_pair = asset_pair

    def get_candles(self, timeframe, from_ts, to_ts):
        response = requests.get(
            f'{MARKET_DATA_ADDRESS}/api/candles/'
            f'{self.asset_pair.a1}/{self.asset_pair.a2}/{timeframe}/{from_ts * 1000}/{to_ts * 1000}')

        candles = []
        for candle in response.json():
            candles.append(Candle(int(candle['timestamp']) // 1000,
                                  float(candle['open']),
                                  float(candle['close']),
                                  float(candle['low']),
                                  float(candle['high'])))
        return self.__fill_gaps(list(reversed(candles)))

    def __fill_gaps(self, candles):
        for index in range(1, len(candles)):
            if candles[index].open == 0:
                candles[index].open = candles[index - 1].open
                candles[index].close = candles[index - 1].close
                candles[index].low = candles[index - 1].low
                candles[index].high = candles[index - 1].high
        return candles
