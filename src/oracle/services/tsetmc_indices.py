import requests
import datetime
import copy
import re
from pytse_client.download import download_financial_indexes

BASE_URL = 'http://www.tsetmc.com/tsev2/chart/data/Index.aspx?i={}&t=value'
indices_info= [
    {
        "day_of_event": "2020-11-18T16:29:00",
        "index_changes": 2979.07031,
        "last_index_value": 69296.54,
        "symbol_isin": "IRX6XS300006",
        "percent_variation": 4.49213457,
        "symbol_title": "شاخص 30 شركت بزرگ",
        "tse_id": "10523825119011581"
    },
    {
        "day_of_event": "2020-11-18T16:00:00",
        "index_changes": 2212.69141,
        "last_index_value": 52684.07,
        "symbol_isin": "IRX6XSLC0006",
        "percent_variation": 4.384049,
        "symbol_title": "شاخص50شركت فعالتر",
        "tse_id": "46342955726788357"
    },
    {
        "day_of_event": "2020-11-18T16:00:00",
        "index_changes": 44709.125,
        "last_index_value": 1185140.88,
        "symbol_isin": "IRX6XSNT0006",
        "percent_variation": 3.92036152,
        "symbol_title": "شاخص صنعت",
        "tse_id": "43754960038275285"
    },
    {
        "day_of_event": "2020-11-18T16:25:00",
        "index_changes": 48347.875,
        "last_index_value": 1345295,
        "symbol_isin": "IRX6XTPI0006",
        "percent_variation": 3.72782755,
        "symbol_title": "شاخص كل",
        "tse_id": "32097828799138957"
    },
    {
        "day_of_event": "2020-11-18T16:25:00",
        "index_changes": 4323.297,
        "last_index_value": 249706.1,
        "symbol_isin": "IRXYXTPI0026",
        "percent_variation": 1.76185942,
        "symbol_title": "شاخص قيمت (هم وزن)",
        "tse_id": "8384385859414435"
    },
    {
        "day_of_event": "2020-11-18T16:10:00",
        "index_changes": 298.259766,
        "last_index_value": 16646.92,
        "symbol_isin": "IRXZXOCI0006",
        "percent_variation": 1.82436967,
        "symbol_title": "شاخص كل فرابورس",
        "tse_id": "32097828799138957"
    },
]

# get_indices_history
def get_indices_history(date_from = None, date_to = None):
    indices_raw = download_financial_indexes(symbols="all")
    indices = []
    for key, value in indices_raw.items():
        if date_from:
            value = value[value['date'] >= date_from]
        if date_to:
            value = value[value['date'] <= date_to]
        indices.append({
            "title":key,
            "dates" : list(value['date']),
            "values": list(value['value'])
        })

    return indices


def ToFloat(item):
    float_pattern = re.compile('\d+\.\d+')
    float_items = float_pattern.findall(item)
    if len(float_items) > 0:
        return float(float_items[0])
    else:
        return 0

# get_live_indices
def get_indices_live():
    indices_info_copy = copy.deepcopy(indices_info)
    for item in indices_info_copy:
        data_all = requests.get(url=BASE_URL.format(item['tse_id']))
        item_current_value = str(data_all.content).split(',')
        if len(item_current_value)>0:
            try:
                item_current_value = item_current_value[-1]
                item_last_value = str(data_all.content).split(',')[-2].split(';')[0]
                item_current_value = ToFloat(item_current_value)
                item_last_value = ToFloat(item_last_value)
            except:
                item_last_value = 0
                item_current_value = 0
            diff  = item_current_value - item_last_value
            item.update({
                "day_of_event": datetime.datetime.now(),
                "index_changes": diff ,
                "last_index_value": item_current_value,
                "percent_variation": 100 * diff/(item_last_value) if item_last_value > 0 else 0,
            })

    return indices_info_copy