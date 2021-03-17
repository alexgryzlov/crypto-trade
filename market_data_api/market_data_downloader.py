import ccxt
import requests
from dateutil.parser import isoparse
from copy import copy
from retry import retry
import typing as tp

from trading import Candle, AssetPair, Timeframe, TimeRange, Timestamp

# API restriction
# https://api.wavesplatform.com/v0/docs/#/candles/getCandles
CANDLES_PER_REQUEST = 1400
MARKET_DATA_HOST = 'https://api.wavesplatform.com'
MATCHER_HOST = "https://matcher.waves.exchange"


class MarketDataDownloader:
    def __init__(self) -> None:
        self.exchange = ccxt.wavesexchange()
        self.exchange.load_markets()

    def get_candles(self, asset_pair: AssetPair, timeframe: Timeframe, time_range: TimeRange) -> tp.List[Candle]:
        candles: tp.List[Candle] = []
        current_ts = time_range.from_ts

        while current_ts <= time_range.to_ts:
            candles_data = self.__load_candles_batch(
                asset_pair=asset_pair,
                timeframe=timeframe,
                time_range=TimeRange(current_ts,
                                     min(current_ts + timeframe.to_seconds() * CANDLES_PER_REQUEST, time_range.to_ts)))

            for candle in candles_data:
                candle_data = candle['data']
                new_candle = Candle(
                    ts=Timestamp.from_iso_format(candle_data['time']),
                    open=candle_data['open'],
                    close=candle_data['close'],
                    low=candle_data['low'],
                    high=candle_data['high'],
                    volume=candle_data['volume'])
                candles.append(new_candle)

            if not candles_data:
                break
            current_ts = candles[-1].ts + 1

        return self.__fill_gaps(candles)

    @retry(RuntimeError, tries=3, delay=2)
    def __load_candles_batch(self, asset_pair: AssetPair, timeframe: Timeframe,
                             time_range: TimeRange) -> tp.List[tp.Dict[str, tp.Any]]:
        asset_pair_id = self.exchange.markets[str(asset_pair)]['id']
        response = requests.get(
            f'{MARKET_DATA_HOST}/v0/candles/{asset_pair_id}',
            params={  # type: ignore
                'interval': timeframe.to_string(),
                'timeStart': self.__to_milliseconds(time_range.from_ts),
                'timeEnd': self.__to_milliseconds(time_range.to_ts)
            })
        if not response:
            raise RuntimeError(response.content)
        return response.json()['data']

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

    def get_orderbook(self, asset_pair: AssetPair, depth: int = 50) -> tp.Dict[str, tp.Any]:
        response = requests.get(
            f'{MATCHER_HOST}/matcher/orderbook/'  # type: ignore
            f'{asset_pair.main_asset.to_waves_format()}/'
            f'{asset_pair.secondary_asset.to_waves_format()}?depth='
            f'{depth}')
        return response.json()
