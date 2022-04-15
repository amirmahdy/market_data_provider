import csv
import os

import requests
from datetime import datetime, timedelta
from typing import List
import re, json

from mdp import settings

TRADE_HISTORY_TODAY_URL = "http://tsetmc.com/tsev2/data/TradeDetail.aspx?i={tse_isin}"
TRADE_HISTORY_YESTERDAY_URL = "http://cdn.tsetmc.com/api/Trade/GetTradeHistory/{tse_isin}/{date}/false"


def get_trades(tse_isin: str, day=None):
    if day is None:
        today = datetime.now().strftime('%Y-%m-%dT')
        url = TRADE_HISTORY_TODAY_URL.format(tse_isin=tse_isin)
        session = requests.Session()
        resp = session.get(url).text
        rgx = (
            "<row>[\s|\r]*<cell>\d*\.?\d*</cell>"
            "[\s|\r]*<cell>(\d*\:\d*\:\d*)</cell>"
            "[\s|\r]*<cell>(\d*\.?\d*)</cell>"
            "[\s|\r]*<cell>(\d*\.?\d*)</cell>"
            "[\s|\r]*</row>"
        )
        all_trades = re.findall(rgx, resp)
        all_trades_dc = []
        for trade in all_trades:
            all_trades_dc.append({"t": (today + trade[0]), "p": int(float(trade[2])), "q": int(float(trade[1]))})
        return all_trades_dc

    else:
        session = requests.Session()
        tse_full_data = session.get(TRADE_HISTORY_YESTERDAY_URL.format(tse_isin=tse_isin, date=day))
        tse_res = json.loads(tse_full_data.text)
        new_history_list = []
        print(tse_res['tradeHistory'])
        file_name_d = str(day)
        day = datetime.strptime(day, '%Y%m%d').strftime('%Y-%m-%dT')
        for item in tse_res['tradeHistory']:
            heven = str(item['hEven'])
            h = heven[0:2] + ":" + heven[2:4] + ":" + heven[4:6]
            new_dict = {
                "t": day + h,  # YYYY-MM-DDTmm:hh:ss
                "q": int(item['qTitTran']),
                "p": int(item['pTran']),
            }
            new_history_list.append(new_dict)
        # Save as CSV

        csv_header = ['t', 'q', 'p']
        file_name = str(file_name_d) + '.csv'

        if not os.path.exists(settings.DATA_ROOT):
            os.mkdir(settings.DATA_ROOT)
        trade_path = settings.DATA_ROOT + '/trade'
        if not os.path.exists(trade_path):
            os.mkdir(trade_path)
        isin_path = trade_path + '/{}'.format(tse_isin)
        if not os.path.exists(isin_path):
            os.mkdir(isin_path)
        csv_path = isin_path + '/' + file_name
        with open(csv_path, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(csv_header)
            for item in new_history_list:
                print(item)
                data = [item["t"], item["q"], item["p"]]
                writer.writerow(data)
        return new_history_list
