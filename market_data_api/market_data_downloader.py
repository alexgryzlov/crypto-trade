import ccxt
import requests
from copy import copy
from retry import retry
import typing as tp

from helpers.typing.common_types import Config

from trading import Candle, AssetPair, Timeframe, TimeRange, Timestamp


class MarketDataDownloader:
    _Config: Config = None
    _Exchange = None

    @staticmethod
    def init(config: Config) -> None:
        MarketDataDownloader._Config = config
        MarketDataDownloader._Exchange = ccxt.wavesexchange()
        # TODO: delete this :)
        MarketDataDownloader._Exchange.verify = False
        MarketDataDownloader._Exchange.load_markets()

    @staticmethod
    def get_candles(asset_pair: AssetPair, timeframe: Timeframe, time_range: TimeRange) -> tp.List[Candle]:
        candles: tp.List[Candle] = []
        current_ts = time_range.from_ts

        while current_ts <= time_range.to_ts:
            candles_data = MarketDataDownloader._load_candles_batch(
                asset_pair=asset_pair,
                timeframe=timeframe,
                time_range=TimeRange(
                    current_ts,
                    min(current_ts + timeframe.to_seconds() * MarketDataDownloader._Config['candles_per_request'],
                        time_range.to_ts)))
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

        return MarketDataDownloader._fill_gaps(candles)

    @staticmethod
    @retry(RuntimeError, tries=3, delay=2)
    def _load_candles_batch(asset_pair: AssetPair, timeframe: Timeframe,
                            time_range: TimeRange) -> tp.List[tp.Dict[str, tp.Any]]:
        asset_pair_id = MarketDataDownloader._Exchange.markets[str(asset_pair)]['id']
        response = requests.get(
            f'{MarketDataDownloader._Config["market_data_host"]}/v0/candles/{asset_pair_id}',
            params={  # type: ignore
                'interval': timeframe.to_string(),
                'timeStart': MarketDataDownloader._to_milliseconds(time_range.from_ts),
                'timeEnd': MarketDataDownloader._to_milliseconds(time_range.to_ts),
            })
        if not response:
            raise RuntimeError(response.content)
        return response.json()['data']

    @staticmethod
    def _to_milliseconds(ts: int) -> int:
        return ts * 1000

    @staticmethod
    def _fill_gaps(candles: tp.List[Candle]) -> tp.List[Candle]:
        for index in range(1, len(candles)):
            if candles[index].open is None:
                ts = candles[index].ts
                candles[index] = copy(candles[index - 1])
                candles[index].ts = ts
        return candles

    @staticmethod
    def get_orderbook(asset_pair: AssetPair, depth: int = 50) -> tp.Dict[str, tp.Any]:
        return MarketDataDownloader._Exchange.fetch_order_book(symbol=str(asset_pair),
                                                               params={'depth': str(depth)})
