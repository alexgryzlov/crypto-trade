import pytest
from dateutil import parser

from market_data_api.market_data_downloader import MarketDataDownloader

from trading import Timeframe, AssetPair, Asset


@pytest.mark.parametrize("timeframe, candle_count", [
    ('15m', 9),
    ('1h', 3)
])
def test_candle_count(timeframe: str, candle_count: int) -> None:
    md_downloader = MarketDataDownloader()
    candles = md_downloader.get_candles(
        asset_pair=AssetPair(Asset('WAVES'), Asset('USDN')),
        timeframe=Timeframe(timeframe),
        from_ts=int(parser.parse('2021-03-01 00:00:00').timestamp()),
        to_ts=int(parser.parse('2021-03-01 02:00:00').timestamp()))
    assert len(candles) == candle_count
