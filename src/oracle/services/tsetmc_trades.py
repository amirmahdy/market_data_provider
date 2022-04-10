import requests
from datetime import datetime, timedelta
from typing import List
import re, json
from oracle.data_type.base import TradeDataType

TRADE_HISTORY_TODAY_URL = "http://tsetmc.com/tsev2/data/TradeDetail.aspx?i={tse_isin}"
TRADE_HISTORY_YESTERDAY_URL = "http://cdn.tsetmc.com/api/Trade/GetTradeHistory/{tse_isin}/{date}/false"


def get_trades(tse_isin: str, day=None) -> List[TradeDataType]:
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
            all_trades_dc.append(TradeDataType(t=(today + trade[0]), p=int(float(trade[2])), q=int(float(trade[1]))))
        return all_trades_dc

    else:
        today = (datetime.strptime(day, '%Y%m%d') - timedelta(days=1)).strftime('%Y-%m-%dT')
        session = requests.Session()
        tse_full_data = session.get(TRADE_HISTORY_YESTERDAY_URL.format(tse_isin=tse_isin, date=day))
        tse_res = json.loads(tse_full_data.text)
        new_history_liat = []
        for item in tse_res['tradeHistory']:
            heven = str(item['hEven'])
            h = heven[0:2] + ":" + heven[2:4] + ":" + heven[4:6]
            new_dict = {
                "t": today + h,  # YYYY-MM-DDTmm:hh:ss
                "q": int(item['qTitTran']),
                "p": int(item['pTran']),
            }
            new_history_liat.append(new_dict)
        # Save as CSV
        return new_history_liat
