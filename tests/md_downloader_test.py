import pytest

from market_data_api.market_data_downloader import MarketDataDownloader

from trading import Timeframe, AssetPair, Asset, TimeRange


@pytest.mark.parametrize("timeframe, candle_count", [
    ('15m', 9),
    ('1h', 3)
])
def test_candle_count(timeframe, candle_count):
    md_downloader = MarketDataDownloader()
    candles = md_downloader.get_candles(
        asset_pair=AssetPair(Asset('WAVES'), Asset('USDN')),
        timeframe=Timeframe(timeframe),
        time_range=TimeRange.from_iso_format(
            from_ts='2021-03-01 00:00:00',
            to_ts='2021-03-01 02:00:00'
        ))
    assert len(candles) == candle_count
