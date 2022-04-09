import requests
import copy
from typing import List, Dict

BESTLIMITS_BASE_URL = "http://cdn.tsetmc.com/api/BestLimits/{isin}/{date}"


def get_askbid_history(tse_isin: str, date: str) -> List[Dict]:
    url = BESTLIMITS_BASE_URL.format(isin=tse_isin, date=date)
    session = requests.Session()
    resp = session.get(url)
    all_askbid_changes = resp.json()['bestLimitsHistory']
    all_askbid_rows = []
    current_captured_askbid = {'time': 0, 'buy_price_1': 0, 'buy_volume_1': 0, 'buy_count_1': 0, 'sell_price_1': 0,
                               'sell_volume_1': 0, 'sell_count_1': 0,
                               'buy_price_2': 0, 'buy_volume_2': 0, 'buy_count_2': 0, 'sell_price_2': 0,
                               'sell_volume_2': 0, 'sell_count_2': 0,
                               'buy_price_3': 0, 'buy_volume_3': 0, 'buy_count_3': 0, 'sell_price_3': 0,
                               'sell_volume_3': 0, 'sell_count_3': 0,
                               'buy_price_4': 0, 'buy_volume_4': 0, 'buy_count_4': 0, 'sell_price_4': 0,
                               'sell_volume_4': 0, 'sell_count_4': 0,
                               'buy_price_5': 0, 'buy_volume_5': 0, 'buy_count_5': 0, 'sell_price_5': 0,
                               'sell_volume_5': 0, 'sell_count_5': 0,
                               }

    for item in all_askbid_changes:
        if item['hEven'] != current_captured_askbid['time'] and current_captured_askbid['time'] != 0:
            all_askbid_rows.append(copy.deepcopy(current_captured_askbid))
        current_captured_askbid['time'] = item['hEven']
        current_captured_askbid['buy_price_{num}'.format(
            num=item['number'])] = item['pMeDem']
        current_captured_askbid['buy_volume_{num}'.format(
            num=item['number'])] = item['qTitMeDem']
        current_captured_askbid['buy_count_{num}'.format(
            num=item['number'])] = item['zOrdMeDem']
        current_captured_askbid['sell_price_{num}'.format(
            num=item['number'])] = item['pMeOf']
        current_captured_askbid['sell_volume_{num}'.format(
            num=item['number'])] = item['qTitMeOf']
        current_captured_askbid['sell_count_{num}'.format(
            num=item['number'])] = item['zOrdMeOf']

    return all_askbid_rows
