'''
При запуске скрипт создает в текущей директории папку с названием
"orderbook_<гггг-мм-дд>", в которой каждую минуту сохраняет csv файлы с данными
из стакана для валютной пары WAVES-USDN. Файлы имеют названия вида
"<чч-мм-сс>.csv". Если в течении работы скрипта наступает следующий день
создаётся новая папка "orderbook_<гггг-мм-дд>" в текущей директории.
'''

import csv
from datetime import datetime
from pathlib import Path

from base.config_parser import ConfigParser
from helpers.getch import getch
from helpers.timeout_decorator import timeout
from market_data_api.market_data_downloader import MarketDataDownloader
from trading.asset import Asset, AssetPair

ASSET_1 = Asset('WAVES')
ASSET_2 = Asset('USDN')
TIME_DELTA = 60  # seconds

base_config = ConfigParser.load_config(Path('configs/base.json'))
MarketDataDownloader.init(base_config)
path = Path.cwd()
today = datetime.today().strftime('%Y-%m-%d')
start_time = datetime.today()
folder = path / ('orderbook_' + today)
counter = 1


def update_folder() -> None:
    global today
    global start_time
    global folder
    global counter
    today = datetime.today().strftime('%Y-%m-%d')
    start_time = datetime.today()
    counter = 1
    folder = path / ('orderbook_' + today)
    folder.mkdir(exist_ok=True)


def load_orderbook() -> None:
    global today
    global start_time
    global folder
    global counter

    print('Loading orderbook... ', end='')
    if today != datetime.today().strftime('%Y-%m-%d'):
        update_folder()
    res = MarketDataDownloader.get_orderbook(AssetPair(ASSET_1, ASSET_2))
    readable_time = \
        datetime.fromtimestamp(res['timestamp'] / 1000).strftime("%H-%M-%S")
    with open(folder / (readable_time + '-bid.csv'), 'w') as f_bid, \
         open(folder / (readable_time + '-ask.csv'), 'w') as f_ask:
        fnames = ['price', 'amount']
        for f, price_type in ((f_bid, 'bids'), (f_ask, 'asks')):
            writer = csv.DictWriter(f, fieldnames=fnames)
            writer.writeheader()
            for row in res[price_type]:
                writer.writerow(dict(zip(fnames, row)))
    counter += 1
    print('Done.')


@timeout(TIME_DELTA)
def read_input() -> None:
    while True:
        if getch() == 'q':
            print('Stopping execution...')
            break


if __name__ == '__main__':
    print('Press `q` to stop downloading orderbook.')
    update_folder()
    load_orderbook()
    while True:
        try:
            read_input()
            break
        except TimeoutError:
            load_orderbook()
