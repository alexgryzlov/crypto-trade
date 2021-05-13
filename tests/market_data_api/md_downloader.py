import pytest

from market_data_api.market_data_downloader import MarketDataDownloader

from helpers.typing.common_types import ConfigsScope


@pytest.fixture(autouse=True)
def market_data_downloader(base_config: ConfigsScope) -> None:
    MarketDataDownloader.init(base_config['market_data_downloader'])
