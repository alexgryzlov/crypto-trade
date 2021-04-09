'''
При запуске скрипт создает в текущей директории папку с названием "orderbook_<гггг-мм-дд>",
в которой каждую минуту сохраняет csv файлы с данными из стакана для валютной пары WAVES-USDN.
Файлы имеют названия вида "<чч-мм-сс>.csv". Если в течении работы скрипта наступает следующий день
создаётся новая папка "orderbook_<гггг-мм-дд>" в текущей директории.
'''

import time
import csv
from datetime import datetime, timedelta
from pathlib import Path
from trading.asset import Asset
from trading.asset import AssetPair
from market_data_api.market_data_downloader import MarketDataDownloader

ASSET_1 = Asset('WAVES')
ASSET_2 = Asset('USDN')
TIME_DELTA = timedelta(minutes=1)

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


update_folder()

while True:
    if today != datetime.today().strftime('%Y-%m-%d'):
        update_folder()
    res = MarketDataDownloader.get_orderbook(AssetPair(ASSET_1, ASSET_2))
    readable_time = datetime.fromtimestamp(res['timestamp'] / 1000).strftime("%H-%M-%S")
    with open(folder / (readable_time + '-bid.csv'), 'w') as f_bid, \
         open(folder / (readable_time + '-ask.csv'), 'w') as f_ask:
        fnames = ['price', 'amount']
        for f, price_type in ((f_bid, 'bids'), (f_ask, 'asks')):
            writer = csv.DictWriter(f, fieldnames=fnames)
            writer.writeheader()
            for row in res[price_type]:
                writer.writerow(dict(zip(fnames, row)))
    time.sleep(((start_time - datetime.today()) + counter * TIME_DELTA).total_seconds())
    counter += 1