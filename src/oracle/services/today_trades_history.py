import requests
from datetime import date
from typing import List
import re
from oracle.data_type.base import TradeDataType

TRADE_HISTORY_BASE_URL = "http://tsetmc.com/tsev2/data/TradeDetail.aspx?i={tse_isin}"


def get_trades(tse_isin: str, day=None) -> List[TradeDataType]:
    url = TRADE_HISTORY_BASE_URL.format(tse_isin=tse_isin)
    session = requests.Session()
    resp = session.get(url).text
    rgx = (
        "<row>[\s|\r]*<cell>\d*\.?\d*</cell>"
        "[\s|\r]*<cell>(\d*\:\d*\:\d*)</cell>"
        "[\s|\r]*<cell>(\d*\.?\d*)</cell>"
        "[\s|\r]*<cell>(\d*\.?\d*)</cell>"
        "[\s|\r]*</row>"
    )
    if day is None:
        today = date.today().strftime('%Y-%m-%dT')
    else:
        today = day

    all_trades = re.findall(rgx, resp)
    all_trades_dc = []
    for trade in all_trades:
        all_trades_dc.append(TradeDataType(t=(today + trade[0]), p=int(float(trade[2])), q=int(float(trade[1]))))
    return all_trades_dc
