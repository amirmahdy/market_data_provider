
def queue_detection(askbid, market_data):

    high_allowed = market_data['high_allowed_price']
    low_allowed = market_data['low_allowed_price']
    last_price = market_data['last_traded_price']

    ask_1 = askbid[0]['best_buy_price']
    bid_1 = askbid[0]['best_sell_price']
    ask_4 = askbid[3]['best_buy_price']
    bid_4 = askbid[3]['best_sell_price']
    ask_5 = askbid[4]['best_buy_price']
    bid_5 = askbid[4]['best_sell_price']

    a = 0.99 * high_allowed
    b = 1.01 * low_allowed
    midp = (ask_1 + bid_1) / 2

    if (high_allowed == bid_1):
        status = 'Is Buy Queue'
    elif (low_allowed == ask_1):
        status = 'Is Sell Queue'
    elif (a <= bid_1 < high_allowed) and (ask_1 != 0):
        if (ask_4 == 0) and (ask_5 == 0):
            status = 'Near Buy Queue'
        elif (last_price >= midp):
            status = 'Near Buy Queue'
    elif (a <= bid_1 < high_allowed) and (ask_1 == 0):
        if (last_price >= bid_1):
            status = 'Near Buy Queue'
    elif (low_allowed < ask_1 <= b) and (bid_1 != 0):
        if (bid_4 == 0) and (bid_5 == 0):
            status = 'Near Sell Queue'
        elif (last_price <= ask_1):
            status = 'Near Sell Queue'
    elif (low_allowed < ask_1 <= b) and (bid_1 == 0):
        if (last_price <= ask_1):
            status = 'Near Sell Queue'
    else:
        status = 'Nothing'

    return status


def check_instrument_queue_status(instrument):
    from oracle.data_type.instrument_market_data import InstrumentData
    from oracle.services.tsetmc_market import get_tse_instrument_data
    from oracle.services.tsetmc_askbid import get_live_askbid
    
    market_data = InstrumentData.get(ref_group="market", isin=instrument.isin)
    if market_data is None:
        market_data = get_tse_instrument_data(instrument, init=True)
    askbid = get_live_askbid(instrument)
    status = queue_detection(askbid, market_data)

    return status


def order_balance(askbid):
    balance_check_multiplier = 1.5
    total_buy_volume = 0
    total_sell_volume = 0

    for i in range(5):
        if askbid[i]['best_buy_quantity'] and askbid[i]['best_buy_quantity'] > 0:
            total_buy_volume = total_buy_volume + askbid[i]['best_buy_quantity']
        if askbid[i]['best_sell_quantity'] and askbid[i]['best_sell_quantity'] > 0:
            total_sell_volume = total_sell_volume + askbid[i]['best_sell_quantity']
        
    # check if each side has higher volume equal to multiplier
    if total_buy_volume > balance_check_multiplier * total_sell_volume:
        return 'Buy Heavier'
    elif total_sell_volume > balance_check_multiplier * total_buy_volume:
        return 'Sell Heavier'
    else:
        return 'Normal'
        
def check_order_balance_status(instrument):
    from oracle.services.tsetmc_askbid import get_live_askbid

    askbid = get_live_askbid(instrument)
    status = order_balance(askbid)

    return status