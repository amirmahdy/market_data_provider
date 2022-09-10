import requests
from pytse_client import Ticker
from mdp.exception_handler import unpredicted_exception_handler, exception_handler

TSETMC_MARKET_URL = "http://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceInfo/{tse_id}"
TSETMC_INSTRUMENTINFO_URL = "http://cdn.tsetmc.com/api/Instrument/GetInstrumentInfo/{tse_id}"
TSETMC_ASKBID_URL = "http://cdn.tsetmc.com/api/BestLimits/{tse_id}"
TSETMC_NAV_URL = "http://cdn.tsetmc.com/api/Fund/GetETFByInsCode/{tse_id}"
def translate_state(item):
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
@unpredicted_exception_handler("DEBUG")
def v(inp, index, ky, default=0):
    if len(inp) > 0:
        return int(getattr(inp[index], ky))
    else:
        return default

@unpredicted_exception_handler("DEBUG")
def get_tse_instrument_data(instrument, init=False):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Host": "cdn.tsetmc.com",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.5",
        "Upgrade-Insecure-Requests": "1"
    }
    market_url = TSETMC_MARKET_URL.format(tse_id = instrument.tse_id)
    instrumentinfo_url = TSETMC_INSTRUMENTINFO_URL.format(tse_id = instrument.tse_id)
    askbid_url = TSETMC_ASKBID_URL.format(tse_id = instrument.tse_id)
    nav_url = TSETMC_NAV_URL.format(tse_id = instrument.tse_id)

    realtime_data = requests.get(market_url, headers=headers)
    instrument_info = requests.get(instrumentinfo_url, headers=headers)
    asbid_data = requests.get(askbid_url, headers=headers)


    realtime_data = realtime_data.json()['closingPriceInfo']
    instrument_info = instrument_info.json()['instrumentInfo']
    asbid_data = asbid_data.json()['bestLimits']
    if init:
        instrument_data = {
            "bid_ask_first_row": {
                "best_buy_price": int(asbid_data[0]['pMeDem']),
                "best_sell_price": int(asbid_data[0]['pMeOf']),
                "best_sell_quantity": int(asbid_data[0]['qTitMeOf']),
                "best_buy_quantity": int(asbid_data[0]['qTitMeDem']),
                "no_best_buy": int(asbid_data[0]['zOrdMeDem']),
                "no_best_sell": int(asbid_data[0]['zOrdMeOf']),
            },
            "symbol_isin": instrument.isin,
            "last_traded_price": int(realtime_data['pDrCotVal']),
            'high_allowed_price': int(instrument_info['staticThreshold']['psGelStaMax']),
            'low_allowed_price': int(instrument_info['staticThreshold']['psGelStaMin']),
            "low_price":  int(realtime_data['priceMin']),
            "high_price":  int(realtime_data['priceMax']),
            'total_number_of_shares_traded': int(realtime_data['qTotTran5J']),
            'company_name': instrument_info['lVal30'],
            'total_number_of_trades': int(realtime_data['zTotTran']),
            'total_trade_value': int(realtime_data['qTotCap']),
            'basis_volume': int(instrument_info['baseVol']),
            'first_traded_price': int(realtime_data['priceFirst']),
            'closing_price': int(realtime_data['pClosing']),
            "reference_price": int(realtime_data['priceYesterday']),
            "market_status": realtime_data['instrumentState']['cEtaval'],
            "tick_size": instrument.tick_size,
            "price_var": float("%.2f" % (100 * (int(realtime_data['pDrCotVal']) - int(realtime_data['priceYesterday'])) / int(realtime_data['priceYesterday']))),
            "price_change": float(realtime_data['priceChange']),
            "closing_price_var": float(
                "%.2f" % (100 * (int(realtime_data['pClosing']) - int(realtime_data['priceYesterday'])) / int(realtime_data['priceYesterday']))),
            "closing_price_change": int(int(realtime_data['pClosing']) - int(realtime_data['priceYesterday'])),
            "max_quantity_order": int(instrument.order_max_size),
            "min_quantity_order": int(instrument.order_min_size),
            "symbol_fa": instrument.symbol,
        }
    else:
        instrument_data = {
            'high_allowed_price': int(instrument_info['staticThreshold']['psGelStaMax']),
            'low_allowed_price': int(instrument_info['staticThreshold']['psGelStaMin']),
            'basis_volume': int(instrument_info['baseVol']),
            'first_traded_price': int(realtime_data['priceFirst']),
            'closing_price': int(realtime_data['pClosing']),
            "market_status": realtime_data['instrumentState']['cEtaval'],
            "max_quantity_order": int(instrument.order_max_size),
            "min_quantity_order": int(instrument.order_min_size),
        }

    if instrument.type.code == 305:
        nav_data = requests.get(nav_url, headers=headers)
        nav_data = nav_data.json()['etf']
        instrument_data.update({
            'nav_value': int(nav_data['pRedTran']),
            'nav_date': str(nav_data['deven']) + 'T' + str(nav_data['hEven']),
        })
    return realtime_data


@unpredicted_exception_handler("DEBUG")
def get_tse_instrument_data_pytse_client(instrument, init=False):
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
            "market_status": translate_state(ticker.state),
            "max_quantity_order": int(instrument.order_max_size),
            "min_quantity_order": int(instrument.order_min_size),
        }

    if instrument.type.code == 305:
        instrument_data.update({
            'nav_value': ticker.nav,
            'nav_date': ticker.nav_date,
        })
    return instrument_data
