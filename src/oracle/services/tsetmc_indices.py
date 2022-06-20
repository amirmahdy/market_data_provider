import requests
import datetime
import copy
import re
from pytse_client.download import download_financial_indexes

BASE_URL = 'http://www.tsetmc.com/Loader.aspx?Partree=151315&Flow=1'
indices = {"10523825119011581": "IRX6XS300006", "43754960038275285": "IRX6XSNT0006",
           "32097828799138957": "IRX6XTPI0006", "8384385859414435": "IRXYXTPI0026",
           "46342955726788357": "IRX6XSLC0006"}

regex = '<tr><td><a.*{index}">(.*)<\\/a>.*\\s\\n<td>(.*)<\\/td>\\s\\n<td>(.*)<\\/td>\\s\\n<td>.*>(.*)<.*<\\/td>\\s\\n<td>.*>(.*)<.*<\\/td>'


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


def _f(flt):
    return float(flt.replace(',', ''))


# get_live_indices
def get_indices_live():
    data_live = requests.get(url=BASE_URL)
    result = []
    for indice in indices:
        res = re.findall(regex.format(index=indice), data_live.text)
        if len(res) > 0:
            res = res[0]
            result.append({
                "IndexChanges": _f(res[3]),
                "LastIndexValue": _f(res[2]),
                "PercentVariation": _f(res[4]),
                "SymbolTitle": res[0],
                "SymbolISIN": indices[indice]
            })

    return result
