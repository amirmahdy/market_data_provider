from pytse.pytse import SymbolData, PyTse
from oracle.data_type.instrument_market_data import InstrumentData


def get_tse_instrument_full_data(tse_isin):
    PyTse.request_timeout = 20  # changing timeout default=30 !apply to all requests
    pytse = PyTse()  # read_symbol_data=True,read_client_type=False
    data = pytse.symbols_data_by_id[tse_isin]
    #
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
    InstrumentData.update(
        instrument_data['symbol_isin'], 'market', instrument_data)
