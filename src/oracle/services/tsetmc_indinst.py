import requests
from mdp.exception_handler import unpredicted_exception_handler, exception_handler

INDINST_BASE_URL = "http://cdn.tsetmc.com/api/ClientType/GetClientType/{tse_id}/1/0"


@unpredicted_exception_handler("DEBUG")
def get_live_indinst(instrument):
    url = INDINST_BASE_URL.format(tse_id=instrument.tse_id)
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
               "Host": "cdn.tsetmc.com",
               "Accept-Encoding": "gzip, deflate",
               "Accept-Language": "en-US,en;q=0.5",
               "Upgrade-Insecure-Requests": "1"
               }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
         return False
    response = response.json()['clientType']
    indinst_initial_data = {
        "symbol_isin": instrument.isin,
        "ind_buy_volume": response['buy_I_Volume'],
        "ind_buy_number": response['buy_CountI'],
        "ind_buy_value": 0,
        "ind_sell_volume": response['sell_I_Volume'],
        "ind_sell_number": response['sell_CountI'],
        "ind_sell_value": 0,

        "ins_buy_volume": response['buy_N_Volume'],
        "ins_buy_number": response['buy_CountN'],
        "ins_buy_value": 0,
        "ins_sell_volume": response['sell_N_Volume'],
        "ins_sell_number": response['sell_CountN'],
        "ins_sell_value": 0,
    }
    return indinst_initial_data
