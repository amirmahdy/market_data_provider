import requests
import copy
from typing import List, Dict

BESTLIMITS_BASE_URL = "http://cdn.tsetmc.com/api/BestLimits/{isin}/{date}"
TODAY_BESTLIMITS_BASE_URL = "http://cdn.tsetmc.com/api/BestLimits/{isin}"


def get_askbid_history(tse_id: str, date: str) -> List[Dict]:
    url = BESTLIMITS_BASE_URL.format(isin=tse_id, date=date)
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
               "Host": "cdn.tsetmc.com",
               "Accept-Encoding": "gzip, deflate",
               "Accept-Language": "en-US,en;q=0.5",
               "Upgrade-Insecure-Requests": "1"
               }
    resp = requests.get(url, headers=headers)
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
        item['hEven'] = ("%06d" % item["hEven"])
        current_captured_askbid['time'] = item['hEven'][0:2] + ":" + item['hEven'][2:4] + ":" + item['hEven'][4:6]
        current_captured_askbid['buy_price_{num}'.format(num=item['number'])] = item['pMeDem']
        current_captured_askbid['buy_volume_{num}'.format(num=item['number'])] = item['qTitMeDem']
        current_captured_askbid['buy_count_{num}'.format(num=item['number'])] = item['zOrdMeDem']
        current_captured_askbid['sell_price_{num}'.format(num=item['number'])] = item['pMeOf']
        current_captured_askbid['sell_volume_{num}'.format(num=item['number'])] = item['qTitMeOf']
        current_captured_askbid['sell_count_{num}'.format(num=item['number'])] = item['zOrdMeOf']

    return all_askbid_rows


def get_live_askbid(instrument):
    url = TODAY_BESTLIMITS_BASE_URL.format(isin=instrument.tse_id)
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
               "Host": "cdn.tsetmc.com",
               "Accept-Encoding": "gzip, deflate",
               "Accept-Language": "en-US,en;q=0.5",
               "Upgrade-Insecure-Requests": "1"
               }
    resp = requests.get(url, headers=headers)
    realtime_data = resp.json()['bestLimits']

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
            askbid_output[i]['no_best_buy'] = int(realtime_data[i]['zOrdMeDem'])
            askbid_output[i]['best_buy_price'] = int(realtime_data[i]['pMeDem'])
            askbid_output[i]['best_buy_quantity'] = int(realtime_data[i]['qTitMeDem'])
        except Exception as e:
            # no order in askbid realtime data so should left empty
            pass
        try:
            askbid_output[i]['no_best_sell'] = int(realtime_data[i]['zOrdMeOf'])
            askbid_output[i]['best_sell_price'] = int(realtime_data[i]['pMeOf'])
            askbid_output[i]['best_sell_quantity'] = int(realtime_data[i]['qTitMeOf'])
        except Exception as e:
            # no order in askbid realtime data so should left empty
            pass
    return askbid_output
