import logging
from dateutil import parser
from datetime import datetime as dt
from mdp.exception_handler import unpredicted_exception_handler

from oracle.enums import (
    QueueConditionOuput,
    OrderBalanceOutput,
    OrderDepthOutput,
    OrderSide,
    RecentTradesOutput,
    TriggerParameterName,
)
from oracle.data_type.instrument_market_data import InstrumentData
from oracle.models import TriggerParameter

logger = logging.getLogger(__name__)


@unpredicted_exception_handler("DEBUG")
def check_instrument_queue_status(instrument):
    market_data = InstrumentData.get(ref_group="market", isin=instrument.isin)
    askbid = InstrumentData.get(ref_group="askbid", isin=instrument.isin)

    status = QueueConditionOuput.NOTHING
    if market_data['high_allowed_price'] == askbid[0]['best_sell_price']:
        status = QueueConditionOuput.IS_BUY_QUEUE
    elif market_data['low_allowed_price'] == askbid[0]['best_buy_price']:
        status = QueueConditionOuput.IS_SELL_QUEUE
    elif (0.99 * market_data['high_allowed_price'] <= askbid[0]['best_sell_price'] < market_data[
        'high_allowed_price']) and (askbid[0]['best_buy_price'] != 0):
        if (askbid[3]['best_buy_price'] == 0) and (askbid[4]['best_buy_price'] == 0):
            status = QueueConditionOuput.NEAR_BUY_QUEUE
        elif market_data['last_traded_price'] >= (askbid[0]['best_buy_price'] + askbid[0]['best_sell_price']) / 2:
            status = QueueConditionOuput.NEAR_BUY_QUEUE
    elif (0.99 * market_data['high_allowed_price'] <= askbid[0]['best_sell_price'] < market_data[
        'high_allowed_price']) and (askbid[0]['best_buy_price'] == 0):
        if market_data['last_traded_price'] >= askbid[0]['best_sell_price']:
            status = QueueConditionOuput.NEAR_BUY_QUEUE
    elif (market_data['low_allowed_price'] < askbid[0]['best_buy_price'] <= 1.01 * market_data[
        'low_allowed_price']) and (askbid[0]['best_sell_price'] != 0):
        if (askbid[3]['best_sell_price'] == 0) and (askbid[4]['best_sell_price'] == 0):
            status = QueueConditionOuput.NEAR_SELL_QUEUE
        elif market_data['last_traded_price'] <= askbid[0]['best_buy_price']:
            status = QueueConditionOuput.NEAR_SELL_QUEUE
    elif (market_data['low_allowed_price'] < askbid[0]['best_buy_price'] <= 1.01 * market_data[
        'low_allowed_price']) and (askbid[0]['best_sell_price'] == 0):
        if market_data['last_traded_price'] <= askbid[0]['best_buy_price']:
            status = QueueConditionOuput.NEAR_SELL_QUEUE

    return status.text.__str__()


@unpredicted_exception_handler("DEBUG")
def check_order_balance_status(instrument):
    askbid = InstrumentData.get(ref_group="askbid", isin=instrument.isin)
    balance_check_multiplier = 1.5
    total_buy_volume = 0
    total_sell_volume = 0

    for i in range(5):
        if askbid[i]['best_buy_quantity'] and askbid[i]['best_buy_quantity'] > 0:
            total_buy_volume = total_buy_volume + askbid[i]['best_buy_quantity']
        if askbid[i]['best_sell_quantity'] and askbid[i]['best_sell_quantity'] > 0:
            total_sell_volume = total_sell_volume + askbid[i]['best_sell_quantity']

    status = None
    # check if each side has higher volume equal to multiplier
    if total_buy_volume > balance_check_multiplier * total_sell_volume:
        status = OrderBalanceOutput.BUY_HEAVIER
    elif total_sell_volume > balance_check_multiplier * total_buy_volume:
        status = OrderBalanceOutput.SELL_HEAVIER
    else:
        status = OrderBalanceOutput.NORMAL
    return status.text.__str__()


@unpredicted_exception_handler("DEBUG")
def order_depth(askbid, side):
    status = None
    try:
        high_depth_threshold = int(TriggerParameter.objects.get(pk=TriggerParameterName.HDT.text_capital).value)
        low_depth_threshold = int(TriggerParameter.objects.get(pk=TriggerParameterName.LDT.text_capital).value)

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


@unpredicted_exception_handler("DEBUG")
def check_buy_order_depth_status(instrument):
    askbid = InstrumentData.get(ref_group="askbid", isin=instrument.isin)
    status = order_depth(askbid, OrderSide.BUY).text.__str__()

    return status


@unpredicted_exception_handler("DEBUG")
def check_sell_order_depth_status(instrument):
    askbid = InstrumentData.get(ref_group="askbid", isin=instrument.isin)
    status = order_depth(askbid, OrderSide.SELL).text.__str__()

    return status


@unpredicted_exception_handler("DEBUG")
def check_recent_trades_status(instrument):
    trades = InstrumentData.get(ref_group="trades", isin=instrument.isin)

    """
    Finds in window trades with time window format of seconds
    returns status values regarding to trades volume
    """

    try:
        high_volume_threshold = int(TriggerParameter.objects.get(pk=TriggerParameterName.HVT.text_capital).value)
        low_volume_threshold = int(TriggerParameter.objects.get(pk=TriggerParameterName.LVT.text_capital).value)
        time_window = int(TriggerParameter.objects.get(pk=TriggerParameterName.ROW.text_capital).value) * 60

        in_window_trades = []
        in_window = True
        i = len(trades) - 1
        now = dt.now()
        while in_window and i >= 0:
            time_diff = (now - parser.parse(trades[i]['t'])).seconds
            if time_diff < 0:
                raise Exception('Invalid trades times')
            elif time_diff < time_window:
                in_window_trades.append(trades[i])
                i = i - 1
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

    return status.text.__str__()
