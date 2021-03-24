'''
При запуске скрипт создает в текущей директории папку с названием "orderbook_<гггг-мм-дд>",
в которой каждую минуту сохраняет csv файлы с данными из стакана для валютной пары WAVES-USDN.
Файлы имеют названия вида "<чч-мм-сс>.csv". Если в течении работы скрипта наступает следующий день
создаётся новая папка "orderbook_<гггг-мм-дд>" в текущей директории.
'''

import time
import os
import csv
import datetime
from trading.asset import Asset
from trading.asset import AssetPair
from market_data_api.market_data_downloader import MarketDataDownloader

ASSET_1 = Asset('USDN')
ASSET_2 = Asset('WAVES')
TIME_DELTA = datetime.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=1, hours=0, weeks=0)

data_downloader = MarketDataDownloader()
path = os.getcwd()
today = datetime.datetime.today().strftime('%Y-%m-%d')
start_time = datetime.datetime.today()
folder = os.path.join(path, 'orderbook_' + today)
counter = 1


def update_folder() -> None:
    global today
    global start_time
    global folder
    global counter
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    start_time = datetime.datetime.today()
    counter = 1
    folder = os.path.join(path, 'orderbook_' + today)
    if not os.path.exists(folder):
        os.mkdir(folder)


update_folder()

while True:
    if today != datetime.datetime.today().strftime('%Y-%m-%d'):
        update_folder()
    res = data_downloader.get_orderbook(AssetPair(ASSET_1, ASSET_2))
    readable_time = time.ctime(int(str(res['timestamp'])[:-3]))
    with open(os.path.join(folder, readable_time.split()[-2].replace(':', '-') + '.csv'), 'w') as f:
        fnames = ['amount', 'price']
        writer = csv.DictWriter(f, fieldnames=fnames)
        writer.writeheader()
        for row in res['bids']:
            writer.writerow(row)
    time.sleep(((start_time - datetime.datetime.today()) + counter * TIME_DELTA).total_seconds())
    counter += 1