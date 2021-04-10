import pytest

from tests.configs import base_config
from helpers.typing.common_types import ConfigsScope

from market_data_api.market_data_downloader import MarketDataDownloader
from trading import Timeframe, AssetPair, Asset, TimeRange


@pytest.mark.parametrize("timeframe, candle_count", [
    ('15m', 9),
    ('1h', 3)
])
def test_candle_count(timeframe: str, candle_count: int, base_config: ConfigsScope) -> None:
    MarketDataDownloader.init(base_config['market_data_downloader'])
    candles = MarketDataDownloader.get_candles(
        asset_pair=AssetPair(Asset('WAVES'), Asset('USDN')),
        timeframe=Timeframe(timeframe),
        time_range=TimeRange.from_iso_format(
            from_ts='2021-03-01 00:00:00',
            to_ts='2021-03-01 02:00:00'
        ))
    assert len(candles) == candle_count
