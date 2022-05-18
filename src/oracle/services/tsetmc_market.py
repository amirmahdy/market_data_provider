from oracle.models import Instrument
from pytse_client import Ticker


def get_tse_instrument_data(instrument):
    ticker = Ticker(symbol='', index=instrument.tse_id)
    realtime_data = ticker.get_ticker_real_time_info_response()

    instrument_data = {
        "bid_ask_first_row": {
            "best_buy_price": int(realtime_data.buy_orders[0].price),
            "best_sell_price": int(realtime_data.sell_orders[0].price),
            "best_sell_quantity": int(realtime_data.sell_orders[0].volume),
            "best_buy_quantity": int(realtime_data.buy_orders[0].volume),
            "no_best_buy": int(realtime_data.buy_orders[0].count),
            "no_best_sell": int(realtime_data.sell_orders[0].count),
        },
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
        "price_var": float("%.2f" % (100 * (ticker.last_price - ticker.yesterday_price) / ticker.yesterday_price)),
        "price_change": int(ticker.last_price - ticker.yesterday_price),
        "closing_price_var": float(
            "%.2f" % (100 * (ticker.adj_close - ticker.yesterday_price) / ticker.yesterday_price)),
        "closing_price_change": int(ticker.adj_close - ticker.yesterday_price),
        "max_quantity_order": int(instrument.order_max_size),
        "min_quantity_order": int(instrument.order_min_size),
        "symbol_fa": instrument.symbol,
    }

    return instrument_data
