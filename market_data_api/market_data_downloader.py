import requests
from copy import copy

from trading.candle import Candle
from trading.asset import AssetPair

MARKET_DATA_ADDRESS = "http://marketdata.wavesplatform.com"


class MarketDataDownloader:
    def get_candles(self, asset_pair: AssetPair, timeframe, from_ts, to_ts):
        response = requests.get(
            f'{MARKET_DATA_ADDRESS}/api/candles/'
            f'{asset_pair.main_asset.to_waves_format()}/'
            f'{asset_pair.secondary_asset.to_waves_format()}/'
            f'{timeframe}/{from_ts * 1000}/{to_ts * 1000}')
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
                ts = candles[index].ts
                candles[index] = copy(candles[index - 1])
                candles[index].ts = ts
        return candles
