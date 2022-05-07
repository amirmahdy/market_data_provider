import copy
from pytse_client.download import download_financial_indexes


# get_live_askbid
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
