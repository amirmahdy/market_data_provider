from pytse_client import Ticker


def get_live_indinst(tse_id: str, symbol_isin):
    ticker = Ticker(symbol='', index=tse_id)
    real_time_data = ticker.get_ticker_real_time_info_response()

    indinst_initial_data = {
        "symbol_isin": symbol_isin,
        "ind_buy_volume": real_time_data.individual_trade_summary.buy_vol,
        "ind_buy_number": real_time_data.individual_trade_summary.buy_count,
        "ind_buy_value": 0,
        "ind_sell_volume": real_time_data.individual_trade_summary.sell_vol,
        "ind_sell_number": real_time_data.individual_trade_summary.sell_count,
        "ind_sell_value": 0,

        "ins_buy_volume": real_time_data.corporate_trade_summary.buy_vol,
        "ins_buy_number": real_time_data.corporate_trade_summary.buy_count,
        "ins_buy_value": 0,
        "ins_sell_volume": real_time_data.corporate_trade_summary.sell_vol,
        "ins_sell_number": real_time_data.corporate_trade_summary.sell_count,
        "ins_sell_value": 0,
    }

    return indinst_initial_data


