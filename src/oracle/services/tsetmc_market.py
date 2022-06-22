from oracle.models import Instrument
from pytse_client import Ticker


def translate_state(item):
    # PYTSE_CLIENT State standard
    # states = {
    #         "I ": "ممنوع",
    #         "A ": "مجاز",
    #         "AG": "مجاز-مسدود",
    #         "AS": "مجاز-متوقف",
    #         "AR": "مجاز-محفوظ",
    #         "IG": "ممنوع-مسدود",
    #         "IS": "ممنوع-متوقف",
    #         "IR": "ممنوع-محفوظ",
    # }

    states = {
        "ممنوع": "I",
        "مجاز": "A",
        "مجاز-مسدود": "AG",
        "مجاز-متوقف": "AS",
        "مجاز-محفوظ": "AR",
        "ممنوع-مسدود": "IG",
        "ممنوع-متوقف": "IS",
        "ممنوع-محفوظ": "IR",
    }
    return states.get(item, None)


# Validating askbid input data
def v(inp, index, ky, default=0):
    if len(inp) > 0:
        return int(getattr(inp[index], ky))
    else:
        return default


def get_tse_instrument_data(instrument, init=False):
    ticker = Ticker(symbol='', index=instrument.tse_id)
    realtime_data = ticker.get_ticker_real_time_info_response()

    if init:
        instrument_data = {
            "bid_ask_first_row": {
                "best_buy_price": v(realtime_data.buy_orders, 0, "price", 0),
                "best_sell_price": v(realtime_data.sell_orders, 0, "price", 0),
                "best_sell_quantity": v(realtime_data.sell_orders, 0, "volume", 0),
                "best_buy_quantity": v(realtime_data.buy_orders, 0, "volume", 0),
                "no_best_buy": v(realtime_data.buy_orders, 0, "count", 0),
                "no_best_sell": v(realtime_data.sell_orders, 0, "count", 0),
            },
            "symbol_isin": instrument.isin,
            "last_traded_price": ticker.last_price,
            'high_allowed_price': ticker.sta_max,
            'low_allowed_price': ticker.sta_min,
            "low_price": int(realtime_data.low_price),
            "high_price": int(realtime_data.high_price),
            'total_number_of_shares_traded': ticker.volume,
            'company_name': ticker.title,
            'total_number_of_trades': ticker.count,
            'total_trade_value': ticker.value,
            'basis_volume': ticker.base_volume,
            'first_traded_price': ticker.open_price,
            'closing_price': ticker.adj_close,
            "reference_price": ticker.yesterday_price,
            "market_status": translate_state(ticker.state),
            "tick_size": instrument.tick_size,
            "price_var": float("%.2f" % (100 * (ticker.last_price - ticker.yesterday_price) / ticker.yesterday_price)),
            "price_change": int(ticker.last_price - ticker.yesterday_price),
            "closing_price_var": float(
                "%.2f" % (100 * (ticker.adj_close - ticker.yesterday_price) / ticker.yesterday_price)),
            "closing_price_change": int(ticker.adj_close - ticker.yesterday_price),
            "max_quantity_order": int(instrument.order_max_size),
            "min_quantity_order": int(instrument.order_min_size),
            "symbol_fa": instrument.symbol,
        }
    else:
        instrument_data = {
            'high_allowed_price': ticker.sta_max,
            'low_allowed_price': ticker.sta_min,
            'basis_volume': ticker.base_volume,
            'first_traded_price': ticker.open_price,
            "reference_price": ticker.yesterday_price,
            "market_status": ticker.state,
            "max_quantity_order": int(instrument.order_max_size),
            "min_quantity_order": int(instrument.order_min_size),
        }

    return instrument_data
