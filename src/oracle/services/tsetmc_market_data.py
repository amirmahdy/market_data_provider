import requests

TSE_DATA_URL = "http://tsetmc.com/tsev2/data/instinfodata.aspx?i={tse_isin}&c=27"


def get_tse_instrument_data(tse_isin):
    session = requests.Session()
    tse_full_data = session.get(TSE_DATA_URL.format(tse_isin=tse_isin)).text.split(',')

    # Seems status for instrument in TSETMC defined as "A " or "IS"
    instrument_data = {
        "reference_price": tse_full_data[5],
        "market_status": "ALLOWED" if tse_full_data[1] == 'A ' else "STOPPED",
        "high_allowed_price": tse_full_data[6],
        "low_allowed_price": tse_full_data[7],
    }
    return instrument_data
