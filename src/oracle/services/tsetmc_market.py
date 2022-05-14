from oracle.models import Instrument
from pytse_client import Ticker


def get_tse_instrument_data(instrument):
    ticker = Ticker(symbol='', index=instrument.tse_id)
    instrument_data = {
        "symbol_isin": instrument.isin,
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
        "tick_size": instrument.tick_size,
        "price_var": float(((ticker.last_price - ticker.yesterday_price) / ticker.yesterday_price) * 100),
        "price_change": int(ticker.last_price - ticker.yesterday_price),
        "max_quantity_order": int(instrument.order_max_size),
        "min_quantity_order": int(instrument.order_min_size),
        "symbol_fa": instrument.symbol,
    }

    return instrument_data
