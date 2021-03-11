import ccxt
import requests
from dateutil.parser import isoparse
from copy import copy
import typing as tp

from trading import Candle, AssetPair, Timeframe

# API restriction
# https://api.wavesplatform.com/v0/docs/#/candles/getCandles
CANDLES_PER_REQUEST = 1400
MARKET_DATA_HOST = 'https://api.wavesplatform.com'


class MarketDataDownloader:
    def __init__(self) -> None:
        self.exchange = ccxt.wavesexchange()
        self.exchange.load_markets()

    def get_candles(self, asset_pair: AssetPair, timeframe: Timeframe,
                    from_ts: int, to_ts: int) -> tp.List[Candle]:
        candles: tp.List[Candle] = []
        current_ts = from_ts

        while current_ts <= to_ts:
            asset_pair_id = self.exchange.markets[str(asset_pair)]['id']
            response = requests.get(
                f'{MARKET_DATA_HOST}/v0/candles/{asset_pair_id}',
                params=tp.cast(tp.Dict[str, str], {
                    'interval': timeframe.to_string(),
                    'timeStart': self.__to_milliseconds(current_ts),
                    'timeEnd': self.__to_milliseconds(
                        min(current_ts +
                            timeframe.to_seconds() * CANDLES_PER_REQUEST,
                            to_ts))
                }))

            if not response:
                raise Exception(response.content)

            for candle in response.json()['data']:
                candle_data = candle['data']
                new_candle = Candle(
                    ts=int(isoparse(candle_data['time']).timestamp()),
                    open_price=candle_data['open'],
                    close_price=candle_data['close'],
                    low_price=candle_data['low'],
                    high_price=candle_data['high'],
                    volume=candle_data['volume'])
                candles.append(new_candle)

            if not candles:
                break
            current_ts = candles[-1].ts + 1

        return self.__fill_gaps(candles)

    @staticmethod
    def __to_milliseconds(ts: int) -> int:
        return ts * 1000

    @staticmethod
    def __fill_gaps(candles: tp.List[Candle]) -> tp.List[Candle]:
        for index in range(1, len(candles)):
            if candles[index].open is None:
                ts = candles[index].ts
                candles[index] = copy(candles[index - 1])
                candles[index].ts = ts
        return candles
