import pywaves as pw
import time
import os
import csv
import datetime

ASSET_1 = 'DG2xFkPdDwKUoBkzGAhQtLpSGzfXLiCYPEzeKH2Ad24p'
ASSET_2 = 'WAVES'
HOST = 'https://matcher.waves.exchange'
TIME_DELTA = datetime.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=1, hours=0, weeks=0)

path = os.getcwd()
today = datetime.datetime.today().strftime('%Y-%m-%d')
start_time = datetime.datetime.today()
folder = os.path.join(path, 'Orderbook_' + today)
counter = 1


def update_folder():
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    start_time = datetime.datetime.today()
    counter = 1
    folder = os.path.join(path, 'Orderbook_' + today)
    if not os.path.exists(folder):
        os.mkdir(folder)


update_folder()

while True:
    if today != datetime.datetime.today().strftime('%Y-%m-%d'):
        update_folder()
    res = pw.wrapper('/matcher/orderbook/%s/%s?depth=50' % (ASSET_1, ASSET_2), host=HOST)
    readable_time = time.ctime(int(str(res['timestamp'])[:-3]))
    with open(os.path.join(folder, readable_time.split()[-2].replace(':', '-') + '.csv'), 'w') as f:
        fnames = ['amount', 'price']
        writer = csv.DictWriter(f, fieldnames=fnames)
        writer.writeheader()
        for row in res['bids']:
            writer.writerow(row)
    time.sleep(((start_time - datetime.datetime.today()) + counter * TIME_DELTA).total_seconds())
    counter += 1

