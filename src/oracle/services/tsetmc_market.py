import requests
from mdp.exception_handler import unpredicted_exception_handler, exception_handler
from datetime import datetime
from oracle.utils import gregorian_to_jdate

TSETMC_MARKET_URL = "http://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceInfo/{tse_id}"
TSETMC_INSTRUMENT_INFO_URL = "http://cdn.tsetmc.com/api/Instrument/GetInstrumentInfo/{tse_id}"
TSETMC_ASK_BID_URL = "http://cdn.tsetmc.com/api/BestLimits/{tse_id}"
TSETMC_NAV_URL = "http://cdn.tsetmc.com/api/Fund/GetETFByInsCode/{tse_id}"


def change_by_yesterday(desired_val, yesterday):
    return float("%.2f" % (100 * (int(desired_val) - int(yesterday)) / int(yesterday)))


def jalali_market_data(market_data):
    date = datetime.strptime(str(market_data['dEven']), '%Y%m%d')
    time = ("%06d" % market_data["hEven"])
    time = ':'.join([time[0:2], time[2:4], time[4:6]])
    jalali_data = gregorian_to_jdate(date)[:10]
    return ' '.join([str(jalali_data), str(time)])


@unpredicted_exception_handler("DEBUG")
def v(inp, index, ky, default=0):
    if len(inp) > 0:
        return int(inp[index].get(ky))
    else:
        return default


@unpredicted_exception_handler("DEBUG")
def get_tse_instrument_data(instrument):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Host": "cdn.tsetmc.com",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.5",
        "Upgrade-Insecure-Requests": "1"
    }
    market_url = TSETMC_MARKET_URL.format(tse_id=instrument.tse_id)
    instrument_info_url = TSETMC_INSTRUMENT_INFO_URL.format(tse_id=instrument.tse_id)
    ask_bid_url = TSETMC_ASK_BID_URL.format(tse_id=instrument.tse_id)
    nav_url = TSETMC_NAV_URL.format(tse_id=instrument.tse_id)

    market_data = requests.get(market_url, headers=headers)
    instrument_data = requests.get(instrument_info_url, headers=headers)
    ask_bid_data = requests.get(ask_bid_url, headers=headers)

    market_data = market_data.json()['closingPriceInfo']
    instrument_data = instrument_data.json()['instrumentInfo']
    ask_bid_data = ask_bid_data.json()['bestLimits']

    instrument_data = {
        # High Frequent data
        "bid_ask_first_row": {
            "best_buy_price": v(ask_bid_data, 0, "pMeDem"),
            "best_sell_price": v(ask_bid_data, 0, "pMeOf"),
            "best_sell_quantity": v(ask_bid_data, 0, "qTitMeOf"),
            "best_buy_quantity": v(ask_bid_data, 0, "qTitMeDem"),
            "no_best_buy": v(ask_bid_data, 0, "zOrdMeDem"),
            "no_best_sell": v(ask_bid_data, 0, "zOrdMeOf"),
        },
        "last_traded_price": int(market_data['pDrCotVal']),
        "closing_price": int(market_data['pClosing']),
        "price_var": change_by_yesterday(market_data['pDrCotVal'], market_data['priceYesterday']),
        "price_change": float(market_data['priceChange']),
        "total_number_of_shares_traded": int(market_data['qTotTran5J']),
        "closing_price_var": change_by_yesterday(market_data['pClosing'], market_data['priceYesterday']),
        "closing_price_change": int(int(market_data['pClosing']) - int(market_data['priceYesterday'])),
        "total_number_of_trades": int(market_data['zTotTran']),
        "total_trade_value": int(market_data['qTotCap']),
        "low_price": int(market_data['priceMin']),
        "high_price": int(market_data['priceMax']),
        "market_status": market_data['instrumentState']['cEtaval'].strip(),
        "first_traded_price": int(market_data['priceFirst']),
        "trade_date": jalali_market_data(market_data),

        # Change by start_day data
        "high_allowed_price": int(instrument_data['staticThreshold']['psGelStaMax']),
        "low_allowed_price": int(instrument_data['staticThreshold']['psGelStaMin']),
        "basis_volume": int(instrument_data['baseVol']),
        "reference_price": int(market_data['priceYesterday']),

        # Long run data
        "max_quantity_order": int(instrument.order_max_size),
        "min_quantity_order": int(instrument.order_min_size),
        "tick_size": instrument.tick_size,
        "company_name": instrument_data['lVal30'],
        "symbol_isin": instrument.isin,
        "symbol_fa": instrument.symbol,
    }

    if instrument.type.code == 305:
        nav_data = requests.get(nav_url, headers=headers)
        nav_data = nav_data.json()['etf']
        instrument_data.update({
            'nav_value': int(nav_data['pRedTran']),
            'nav_date': str(nav_data['deven']) + 'T' + str(nav_data['hEven']),
        })
    return instrument_data
