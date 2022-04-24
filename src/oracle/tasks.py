from datetime import datetime
from tkinter import E
from celery import shared_task
from oracle.models import Instrument
from oracle.data_type.instrument_market_data import InstrumentData
from oracle.cache.base import Cache
from oracle.services.tsetmc_market import get_tse_instrument_data
from oracle.services.tsetmc_trades import get_trades
from oracle.services.tsetmc_askbid import get_askbid_history
from datetime import datetime, timedelta
from oracle.triggers.queue_condition import check_instrument_queue_status
from morpheus.services.broadcast import broadcast_trigger, broadcast_market_data

cache = Cache()


@shared_task(name="tsetmc_market_data_update")
def market_data_update():
    try:
        instruments = Instrument.get_instruments()
        for instrument in instruments:
            res = get_tse_instrument_data(instrument.tse_id)
            InstrumentData.update(instrument.isin, "market", res)

            # update market status
            if res['market_status'] != instrument.market_status:
                instrument.market_status = res['market_status']
                instrument.save()
                broadcast_trigger(
                    isin=instrument.isin, data={'trigger_type': 'instrument_market_status_change'})
                broadcast_market_data(isin=instrument.isin,
                                      market_data=InstrumentData.get(isin=instrument.isin, ref_group='market'))

    except Exception as e:
        print(e)
        return e
    return True


@shared_task(name="tsetmc_askbid_yesterday_update")
def tsetmc_askbid_yesterday_update():
    try:
        instruments = Instrument.get_instruments()
        yesterday = datetime.strftime(datetime.now() - timedelta(1), '%Y%m%d')
        for instrument in instruments:
            today_trades = get_askbid_history(instrument.tse_id, yesterday)
            print(today_trades)
    except Exception as e:
        print(e)
        return e
    return True


@shared_task(name="tsetmc_trade_yesterday_update")
def trade_data_yesterday_update():
    try:
        instruments = Instrument.get_instruments()
        yesterday = datetime.strftime(datetime.now() - timedelta(1), '%Y%m%d')
        for instrument in instruments:
            today_trades = get_trades(instrument.tse_id, yesterday)
            print(today_trades)
    except Exception as e:
        print(e)
        return e
    return True


@shared_task(name="tsetmc_trade_today_update")
def trade_data_today_update():
    try:
        instruments = Instrument.get_instruments()
        for instrument in instruments:
            today_trades = get_trades(instrument.tse_id)
            InstrumentData.update(instrument.isin, 'trades', today_trades)
    except Exception as e:
        print(e)
        return e
    return True


@shared_task(name='check_queue_condition')
def check_queue_condition():
    try:
        instruments = Instrument.get_instruments()
        for instrument in instruments:
            check_instrument_queue_status(instrument.isin)
    except Exception as e:
        print(e)
        return e
    return True
