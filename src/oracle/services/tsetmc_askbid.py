import requests
import copy
from typing import List, Dict
from pytse_client import Ticker

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


def get_live_askbid(tse_id: str):
    ticker = Ticker(symbol='', index=tse_id)
    realtime_data = ticker.get_ticker_real_time_info_response()

    askbid_output = []
    empty_askbid_row = {
        "no_best_buy": 0,
        "best_buy_price": 0,
        "best_sell_price": 0,
        "best_buy_quantity": 0,
        "best_sell_quantity": 0,
        "no_best_sell": 0,
    }
    for i in range(5):
        askbid_output.append(copy.deepcopy(empty_askbid_row))
        try:
            askbid_output[i]['no_best_buy'] = int(realtime_data.buy_orders[i].count)
            askbid_output[i]['best_buy_price'] = int(realtime_data.buy_orders[i].price)
            askbid_output[i]['best_buy_quantity'] = int(realtime_data.buy_orders[i].volume)
        except Exception as e:
            # no order in askbid realtime data so should left empty
            pass
        try:
            askbid_output[i]['no_best_sell'] = int(realtime_data.sell_orders[i].count)
            askbid_output[i]['best_sell_price'] = int(realtime_data.sell_orders[i].price)
            askbid_output[i]['best_sell_quantity'] = int(realtime_data.sell_orders[i].volume)
        except Exception as e:
            # no order in askbid realtime data so should left empty
            pass
    return askbid_output
