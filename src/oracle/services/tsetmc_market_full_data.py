from pytse.pytse import PyTse
from oracle.data_type.instrument_market_data import InstrumentData


def get_tse_instrument_full_data(isin, tse_isin):
    PyTse.request_timeout = 20
    pytse = PyTse()
    data = pytse.symbols_data_by_id[tse_isin]
    instrument_data = {
        "symbol_isin": data['l18'],
        "last_traded_price": data['pl'],
        'high_allowed_price': data['tmax'],
        'low_allowed_price': data['tmin'],
        'total_number_of_shares_traded': data['tvol'],
        'company_name': data['l30'],
        'total_number_of_trades': data['tno'],
        'total_trade_value': data['tval'],
        'basis_volume': data['bvol'],
        'symbol_group_code': data['cs'],
        'first_traded_price': data['pf'],
        'closing_price': data['pc'],
        'closing_price_change': data['pcc']
    }
    InstrumentData.update(isin, 'market', instrument_data)


def initial_setup():
    from oracle.models import Instrument
    instruments = Instrument.get_instruments()
    for instrument in instruments:
        get_tse_instrument_full_data(instrument, instruments[instrument].tse_id)
