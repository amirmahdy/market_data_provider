from oracle.models import Instrument
from pytse_client import Ticker


def get_tse_instrument_data(tse_isin: str):
    ticker = Ticker(symbol='', index=tse_isin)
    symbol_isin = None
    try:
        symbol_isin = Instrument.objects.get(tse_id=tse_isin).isin
    except:
        pass
    instrument_data = {
        "symbol_isin": symbol_isin,
        "last_traded_price": ticker.last_price,
        'high_allowed_price': ticker.sta_max,
        'low_allowed_price': ticker.sta_min,
        'total_number_of_shares_traded': ticker.volume,
        'company_name': ticker.title,
        'total_number_of_trades': ticker.count,
        'total_trade_value': ticker.value,
        'basis_volume': ticker.base_volume,
        'first_traded_price': ticker.open_price,
        'closing_price': ticker.adj_close,
        "reference_price": ticker.yesterday_price,
        "market_status": ticker.state,
    }

    return instrument_data
