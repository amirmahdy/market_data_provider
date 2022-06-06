import environ
from celery import shared_task
from mdp import settings
import fsutil
import zipfile
from mdp.utils import create_csv, create_zip_on_csv
from oracle.models import Instrument
from oracle.data_type.instrument_market_data import InstrumentData
from oracle.cache.base import Cache
from oracle.services.tsetmc_market import get_tse_instrument_data, translate_state
from oracle.services.tsetmc_trades import get_trades, get_kline, get_tick_data
from oracle.services.tsetmc_askbid import get_askbid_history
from datetime import datetime, timedelta
from oracle.triggers.queue_condition import broadcast_instrument_queue_status
from morpheus.services.broadcast import broadcast_trigger, broadcast_market_data

cache = Cache()
env = environ.Env()


@shared_task(name="tsetmc_market_data_update")
def market_data_update():
    try:
        instruments = Instrument.get_instruments()
        for instrument in instruments:
            res = get_tse_instrument_data(instrument)
            InstrumentData.update(instrument.isin, "market", res)

            # update market status
            if res['market_status'] != instrument.market_status:
                instrument.market_status = res['market_status']
                instrument.save()
                instrument_state = {'state': res['market_status'], 'stateCode' : translate_state(res['market_status'])}
                InstrumentData.update(instrument.isin, 'state', instrument_state)
                broadcast_trigger(isin=instrument.isin, data={'trigger_type': 'instrument_market_status_change'})
                broadcast_market_data(isin=instrument.isin,
                                      market_data=InstrumentData.get(isin=instrument.isin, ref_group='market'))

    except Exception as e:
        print(e)
        return e
    return True


@shared_task(name="tsetmc_askbid_yesterday_update")
def tsetmc_askbid_yesterday_update(days):
    try:
        instruments = Instrument.get_instruments()
        for day in range(1, days + 1):
            yesterday = datetime.strftime(datetime.now() - timedelta(day), '%Y%m%d')
            path = settings.DATA_ROOT + "/askbid/"
            for instrument in instruments:
                today_askbids = get_askbid_history(instrument.tse_id, yesterday)
                if today_askbids:
                    sym = instrument.en_symbol.lower()
                    create_csv(path + sym + "/" + yesterday + ".csv", today_askbids,
                               fieldnames=["time", "buy_price_1", "buy_volume_1", "buy_count_1", "sell_price_1",
                                           "sell_volume_1", "sell_count_1", "buy_price_2", "buy_volume_2",
                                           "buy_count_2",
                                           "sell_price_2", "sell_volume_2", "sell_count_2", "buy_price_3",
                                           "buy_volume_3",
                                           "buy_count_3", "sell_price_3", "sell_volume_3", "sell_count_3",
                                           "buy_price_4",
                                           "buy_volume_4", "buy_count_4", "sell_price_4", "sell_volume_4",
                                           "sell_count_4",
                                           "buy_price_5", "buy_volume_5", "buy_count_5", "sell_price_5",
                                           "sell_volume_5",
                                           "sell_count_5"], frmt="w+")


    except Exception as e:
        print(e)
        return e
    return True


@shared_task(name="tsetmc_trade_yesterday_update")
def trade_data_yesterday_update(days):
    try:
        instruments = Instrument.get_instruments()
        for day in range(1, days + 1):
            yesterday = datetime.strftime(datetime.now() - timedelta(day), '%Y%m%d')
            path = settings.DATA_ROOT + "/trade/"
            for instrument in instruments:
                today_trades = get_trades(instrument.tse_id, yesterday)
                if today_trades:
                    sym = instrument.en_symbol.lower()
                    create_csv(path + sym + "/" + yesterday + ".csv", today_trades,
                               fieldnames=['t', 'q', 'p'], frmt="w+")

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


@shared_task(name="tsetmc_trade_kline")
def tsetmc_trade_kline(days):
    try:
        instruments = Instrument.get_instruments()
        to_date = datetime.strftime(datetime.now(), '%Y%m%d')
        from_date = datetime.strftime(datetime.now() - timedelta(days), '%Y%m%d')
        path = settings.DATA_ROOT + "/equity/usa/daily/"

        for instrument in instruments:
            rows = get_kline(from_date, to_date, instrument.tse_id, env("TSETMC_USERNAME"), env("TSETMC_PASSWORD"))
            sym = instrument.en_symbol

            if fsutil.exists(path + sym.lower() + ".zip"):
                zipfile.ZipFile(path + sym.lower() + ".zip", "r").extractall(path)
                fsutil.remove_file(path + sym.lower() + ".zip")

            create_csv(path + sym.upper() + ".csv", rows, fieldnames=None, frmt="a")
            zipfile.ZipFile(path + sym.lower() + ".zip", "w", zipfile.ZIP_DEFLATED). \
                write(path + sym.upper() + ".csv", arcname=sym.upper() + ".csv")
            fsutil.remove_file(path + sym.upper() + ".csv")

    except Exception as e:
        print(e)
        return e
    return True


@shared_task(name="trade_tick_data")
def trade_tick_data():
    try:
        instruments = Instrument.get_instruments()
        cur_date = datetime.strftime(datetime.now() - timedelta(1), '%Y%m%d')
        for instrument in instruments:
            rows = get_tick_data(instrument.tse_id, cur_date)
            sym = instrument.en_symbol
            path = settings.DATA_ROOT + "/equity/usa/tick/" + sym.upper() + "/"
            zip_filename = cur_date + "_trade.zip"
            csv_filename = cur_date + "_trade.csv"
            create_zip_on_csv(path, zip_filename, csv_filename, rows)
    except Exception as e:
        print(e)
        return e
    return True


@shared_task(name='check_queue_condition')
def check_queue_condition():
    try:
        instruments = Instrument.get_instruments()
        for instrument in instruments:
            broadcast_instrument_queue_status(instrument)
    except Exception as e:
        print(e)
        return e
    return True
