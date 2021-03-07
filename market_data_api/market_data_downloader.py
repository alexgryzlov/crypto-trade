import ccxt
import requests
from dateutil.parser import isoparse
from copy import copy

from trading import Candle, AssetPair, Timeframe

# API restriction
# https://api.wavesplatform.com/v0/docs/#/candles/getCandles
CANDLES_PER_REQUEST = 1400
MARKET_DATA_HOST = 'https://api.wavesplatform.com'


class MarketDataDownloader:
    def __init__(self):
        self.exchange = ccxt.wavesexchange()
        self.exchange.load_markets()

    def get_candles(self, asset_pair: AssetPair, timeframe: Timeframe, from_ts, to_ts):
        candles = []
        current_ts = from_ts

        while current_ts <= to_ts:
            asset_pair_id = self.exchange.markets[str(asset_pair)]['id']
            response = requests.get(
                f'{MARKET_DATA_HOST}/v0/candles/{asset_pair_id}',
                params={
                    'interval': timeframe.to_string(),
                    'timeStart': self.__to_milliseconds(current_ts),
                    'timeEnd': self.__to_milliseconds(
                        min(current_ts + timeframe.to_seconds() * CANDLES_PER_REQUEST, to_ts))
                })

            if not response:
                raise Exception(response.content)

            for candle in response.json()['data']:
                candle_data = candle['data']
                new_candle = Candle(
                    ts=int(isoparse(candle_data['time']).timestamp()),
                    open=candle_data['open'],
                    close=candle_data['close'],
                    low=candle_data['low'],
                    high=candle_data['high'],
                    volume=candle_data['volume'])
                candles.append(new_candle)

            if not len(candles):
                break
            current_ts = candles[-1].ts + 1

        return self.__fill_gaps(candles)

    @staticmethod
    def __to_milliseconds(ts):
        return ts * 1000

    @staticmethod
    def __fill_gaps(candles):
        for index in range(1, len(candles)):
            if candles[index].open is None:
                ts = candles[index].ts
                candles[index] = copy(candles[index - 1])
                candles[index].ts = ts
        return candles
