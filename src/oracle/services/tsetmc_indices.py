import requests
import datetime
import copy
import re
from pytse_client.download import download_financial_indexes

BASE_URL = 'http://www.tsetmc.com/Loader.aspx?Partree=151315&Flow=1'
indices_info = [
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
# regex
float_pattern = re.compile('\(?\d+\.?\d+')
tr_pattern = re.compile(r'<tr>(.*?)</tr>')
td_pattern = re.compile(r'<td>(.*?)</td>')
a_pattern = re.compile(r'>(.*?)</a>')
th_pattern = re.compile(r'<th>([^>]+)</th>')
tse_id_patttern = re.compile('\d{10,}')


# get_indices_history
def get_indices_history(date_from=None, date_to=None):
    indices_raw = download_financial_indexes(symbols="all")
    indices = []
    for key, value in indices_raw.items():
        if date_from:
            value = value[value['date'] >= date_from]
        if date_to:
            value = value[value['date'] <= date_to]
        indices.append({
            "title": key,
            "dates": list(value['date']),
            "values": list(value['value'])
        })

    return indices


def ToFloat(item):
    float_items = float_pattern.findall(item.replace(',', ''))
    if len(float_items) > 0:
        if float_items[0].find('(') == -1:
            return float(float_items[0])
        else:
            return 0 - float(float_items[0][1:])
    else:
        return 0


# get_live_indices
def get_indices_live():
    template = {
        "DayOfEvent": "2020-11-18T16:10:00",
        "IndexChanges": 298.259766,
        "LastIndexValue": 16646.92,
        "SymbolISIN": "IRXZXOCI0006",
        "PercentVariation": 1.82436967,
        "SymbolTitle": "شاخص كل فرابورس",
        "TseId": "32097828799138957"
    }
    data_live = requests.get(url=BASE_URL)
    data_live_processed = tr_pattern.findall(re.sub('\s+', ' ', data_live.text))
    indices = []

    for row in data_live_processed:
        cells = td_pattern.findall(row)
        if len(cells) > 0:
            title = a_pattern.findall(cells[0])
            id = tse_id_patttern.findall(cells[0])
            id = id[0] if len(id) > 0 else ""
            isin_data = [item for item in indices_info if item['tse_id'] == id]
            isin_data = isin_data[0]["symbol_isin"] if len(isin_data) > 0 else ""
            if isin_data != "":
                indices.append({
                    "DayOfEvent": str(datetime.datetime.today().date()) + 'T' + str(cells[1]),
                    "IndexChanges": ToFloat(cells[3]),
                    "LastIndexValue": ToFloat(cells[2]),
                    "PercentVariation": ToFloat(cells[4]),
                    "SymbolTitle": title[0] if len(title) > 0 else "",
                    "TseId": id,
                    "SymbolISIN": isin_data
                })

    return indices
