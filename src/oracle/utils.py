import logging
import queue
from dateutil import parser
from datetime import datetime as dt

from oracle.models import TriggerParameter

logger = logging.getLogger(__name__)

def queue_detection(askbid, market_data):
    from .enums import QueueConditionOuput

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

    status = QueueConditionOuput.NOTHING
    if (high_allowed == bid_1):
        status = QueueConditionOuput.IS_BUY_QUEUE
    elif (low_allowed == ask_1):
        status = QueueConditionOuput.IS_SELL_QUEUE
    elif (a <= bid_1 < high_allowed) and (ask_1 != 0):
        if (ask_4 == 0) and (ask_5 == 0):
            status = QueueConditionOuput.NEAR_BUY_QUEUE
        elif (last_price >= midp):
            status = QueueConditionOuput.NEAR_BUY_QUEUE
    elif (a <= bid_1 < high_allowed) and (ask_1 == 0):
        if (last_price >= bid_1):
            status = QueueConditionOuput.NEAR_BUY_QUEUE
    elif (low_allowed < ask_1 <= b) and (bid_1 != 0):
        if (bid_4 == 0) and (bid_5 == 0):
            status = QueueConditionOuput.NEAR_SELL_QUEUE
        elif (last_price <= ask_1):
            status = QueueConditionOuput.NEAR_SELL_QUEUE
    elif (low_allowed < ask_1 <= b) and (bid_1 == 0):
        if (last_price <= ask_1):
            status = QueueConditionOuput.NEAR_SELL_QUEUE

    return status


def check_instrument_queue_status(instrument):
    from oracle.data_type.instrument_market_data import InstrumentData
    from oracle.services.tsetmc_market import get_tse_instrument_data
    from oracle.services.tsetmc_askbid import get_live_askbid
    
    market_data = InstrumentData.get(ref_group="market", isin=instrument.isin)
    if market_data is None:
        market_data = get_tse_instrument_data(instrument, init=True)
    askbid = get_live_askbid(instrument.tse_id)
    status = queue_detection(askbid, market_data).text.__str__()

    return status


def order_balance(askbid):
    from .enums import OrderBalanceOutput

    balance_check_multiplier = 1.5
    total_buy_volume = 0
    total_sell_volume = 0

    for i in range(5):
        if askbid[i]['best_buy_quantity'] and askbid[i]['best_buy_quantity'] > 0:
            total_buy_volume = total_buy_volume + askbid[i]['best_buy_quantity']
        if askbid[i]['best_sell_quantity'] and askbid[i]['best_sell_quantity'] > 0:
            total_sell_volume = total_sell_volume + askbid[i]['best_sell_quantity']
    
    status =  None
    # check if each side has higher volume equal to multiplier
    if total_buy_volume > balance_check_multiplier * total_sell_volume:
        status = OrderBalanceOutput.BUY_HEAVIER
    elif total_sell_volume > balance_check_multiplier * total_buy_volume:
        status = OrderBalanceOutput.SELL_HEAVIER
    else:
        status = OrderBalanceOutput.NORMAL
    return status


def check_order_balance_status(instrument):
    from oracle.services.tsetmc_askbid import get_live_askbid

    askbid = get_live_askbid(instrument.tse_id)
    status = order_balance(askbid).text.__str__()

    return status

def order_depth(askbid, side):
    from oracle.models import TriggerParameter
    from .enums import OrderDepthOutput, OrderSide

    try:
        high_depth_threshold = int(TriggerParameter.objects.get(name_en='high depth threshold').value)
        low_depth_threshold = int(TriggerParameter.objects.get(name_en='low depth threshold').value)
    
        status = None
        if side == OrderSide.BUY:
            total_buy_volume = 0
            for i in range(5):
                if askbid[i]['best_buy_quantity']:
                   total_buy_volume = total_buy_volume + askbid[i]['best_buy_quantity']

            if total_buy_volume == 0:
                status = OrderDepthOutput.NONE
            elif total_buy_volume > high_depth_threshold:
                status = OrderDepthOutput.HEAVY
            elif total_buy_volume < low_depth_threshold:
                status = OrderDepthOutput.LIGHT
            else:
                status = OrderDepthOutput.NORMAL
            
        elif side == OrderSide.SELL:
            total_sell_volume = 0
            for i in range(5):
                if askbid[i]['best_sell_quantity']:
                   total_sell_volume = total_sell_volume + askbid[i]['best_sell_quantity']

            if total_sell_volume == 0:
                status = OrderDepthOutput.NONE
            elif total_sell_volume > high_depth_threshold:
                status = OrderDepthOutput.HEAVY
            elif total_sell_volume < low_depth_threshold:
                status = OrderDepthOutput.LIGHT
            else:
                status = OrderDepthOutput.NORMAL

    except Exception as e:
        logger.error(f'Error in order depth trigger examiner method: {e.__str__}')

    return status

def check_buy_order_depth_status(instrument):
    from oracle.services.tsetmc_askbid import get_live_askbid
    from .enums import OrderSide


    askbid = get_live_askbid(instrument.tse_id)
    status = order_depth(askbid, OrderSide.BUY).text.__str__()

    return status


def check_sell_order_depth_status(instrument):
    from oracle.services.tsetmc_askbid import get_live_askbid
    from .enums import OrderSide


    askbid = get_live_askbid(instrument.tse_id)
    status = order_depth(askbid, OrderSide.SELL).text.__str__()

    return status


def recent_trades(trades):
    """
    Finds in window trades with time window format of seconds
    returns status values regarding to trades volume
    """
    from .enums import RecentTradesOutput

    try:
        high_volume_threshold = int(TriggerParameter.objects.get(name_en='high volume threshold').value)
        low_volume_threshold = int(TriggerParameter.objects.get(name_en='high volume threshold').value)
        time_window = int(TriggerParameter.objects.get(name_en='rolling window').value) * 60

        in_window_trades = []
        in_window = True
        i = len(trades)-1
        now = dt.now()
        while in_window and i >= 0:
            time_diff = (now - parser.parse(trades[i]['t'])).seconds
            if time_diff < 0:
                raise Exception('Invalid trades times')
            elif time_diff < time_window:
                in_window_trades.append(trades[i])
                i = i-1
            else:
                in_window = False
    except Exception as e:
        logger.error(e.__str__)
        return False

    status = None
    total_volume = 0
    for _ in in_window_trades:
        total_volume = total_volume + _['q']

    if total_volume > high_volume_threshold:
        status = RecentTradesOutput.HIGH
    elif total_volume < low_volume_threshold:
        status = RecentTradesOutput.LOW
    else:
        status = RecentTradesOutput.NORMAL

    return status

def check_recent_trades_status(instrument):
    from oracle.services.tsetmc_trades import get_trades

    trades = get_trades(instrument)
    status = recent_trades(trades).text.__str__()

    return status