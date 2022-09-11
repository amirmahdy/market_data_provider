import environ
from celery import shared_task
from mdp import settings
import fsutil
import zipfile
from mdp.utils import create_csv, create_zip_on_csv
from oracle.data_type.heart_beat import HeartBeat
from oracle.models import Instrument
from oracle.data_type.instrument_market_data import InstrumentData
from oracle.cache.base import Cache
from oracle.services.tsetmc_market import get_tse_instrument_data
from oracle.services.tsetmc_trades import get_trades, get_kline, get_tick_data
from oracle.services.tsetmc_askbid import get_askbid_history
from datetime import datetime, timedelta
from oracle.triggers import (
    broadcast_instrument_queue_status,
    broadcast_order_balance_status,
    broadcast_order_depth_status,
    broadcast_recent_trades_status,
)
from morpheus.services.broadcast import broadcast_trigger, broadcast_market_data
from mdp.exception_handler import unpredicted_exception_handler, exception_handler
import inspect

cache = Cache()
env = environ.Env()
source = "TSETMC"


@shared_task(name="tsetmc_market_data_update")
@unpredicted_exception_handler("DEBUG")
def market_data_update():
    instruments = Instrument.get_instruments()
    for instrument in instruments:
        try:
            res = get_tse_instrument_data(instrument)
            InstrumentData.update(instrument.isin, "market", res)
            HeartBeat.update(source, 'market')

            # update market status
            if instrument.market_status is not None and res['market_status'] != instrument.market_status:
                instrument.market_status = res['market_status']
                instrument.save()
                instrument_state = {'state': res['market_status']}
                InstrumentData.update(instrument.isin, 'state', instrument_state)
                HeartBeat.update(source, 'state')
                broadcast_trigger(isin=instrument.isin, data={'trigger_type': 'instrument_market_status_change'})
                broadcast_market_data(isin=instrument.isin,
                                      market_data=InstrumentData.get(isin=instrument.isin, ref_group='market'))
        except Exception:
            exception_handler("DEBUG", inspect.currentframe())
    return True


@shared_task(name="tsetmc_askbid_yesterday_update")
@unpredicted_exception_handler("DEBUG")
def tsetmc_askbid_yesterday_update(days):
    instruments = Instrument.get_instruments()
    for day in range(1, days + 1):
        yesterday = datetime.strftime(datetime.now() - timedelta(day), '%Y%m%d')
        path = settings.DATA_ROOT + "/askbid/"
        for instrument in instruments:
            try:
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
            except Exception:
                exception_handler("DEBUG", inspect.currentframe())
    return True


@shared_task(name="tsetmc_trade_yesterday_update")
@unpredicted_exception_handler("DEBUG")
def trade_data_yesterday_update(days):
    instruments = Instrument.get_instruments()
    for day in range(1, days + 1):
        yesterday = datetime.strftime(datetime.now() - timedelta(day), '%Y%m%d')
        path = settings.DATA_ROOT + "/trade/"
        for instrument in instruments:
            try:
                today_trades = get_trades(instrument, yesterday)
                if today_trades:
                    sym = instrument.en_symbol.lower()
                    create_csv(path + sym + "/" + yesterday + ".csv", today_trades,
                               fieldnames=['t', 'q', 'p'], frmt="w+")
            except Exception:
                exception_handler("DEBUG", inspect.currentframe())
    return True


@shared_task(name="tsetmc_trade_today_update")
@unpredicted_exception_handler("DEBUG")
def trade_data_today_update():
    instruments = Instrument.get_instruments()
    for instrument in instruments:
        try:
            today_trades = get_trades(instrument)
            InstrumentData.update(instrument.isin, 'trades', today_trades)
            HeartBeat.update(source, 'trades')
        except Exception:
            exception_handler("DEBUG", inspect.currentframe())
    return True


@shared_task(name="tsetmc_trade_kline")
@unpredicted_exception_handler("DEBUG")
def tsetmc_trade_kline(days):
    instruments = Instrument.get_instruments()
    to_date = datetime.strftime(datetime.now(), '%Y%m%d')
    from_date = datetime.strftime(datetime.now() - timedelta(days), '%Y%m%d')
    path = settings.DATA_ROOT + "/equity/usa/daily/"

    for instrument in instruments:
        try:
            rows = get_kline(from_date, to_date, instrument.tse_id, env("TSETMC_USERNAME"), env("TSETMC_PASSWORD"))
            sym = instrument.en_symbol

            if fsutil.exists(path + sym.lower() + ".zip"):
                zipfile.ZipFile(path + sym.lower() + ".zip", "r").extractall(path)
                fsutil.remove_file(path + sym.lower() + ".zip")

            create_csv(path + sym.upper() + ".csv", rows, fieldnames=None, frmt="a")
            zipfile.ZipFile(path + sym.lower() + ".zip", "w", zipfile.ZIP_DEFLATED). \
                write(path + sym.upper() + ".csv", arcname=sym.upper() + ".csv")
            fsutil.remove_file(path + sym.upper() + ".csv")
        except Exception:
            exception_handler("DEBUG", inspect.currentframe())

    return True


@shared_task(name="trade_tick_data")
@unpredicted_exception_handler("DEBUG")
def trade_tick_data():
    instruments = Instrument.get_instruments()
    cur_date = datetime.strftime(datetime.now() - timedelta(1), '%Y%m%d')
    for instrument in instruments:
        try:
            rows = get_tick_data(instrument.tse_id, cur_date)
            if rows:
                sym = instrument.en_symbol
                path = settings.DATA_ROOT + "/equity/usa/tick/" + sym.upper() + "/"
                zip_filename = cur_date + "_trade.zip"
                csv_filename = cur_date + "_trade.csv"
                create_zip_on_csv(path, zip_filename, csv_filename, rows)
        except Exception:
            exception_handler("DEBUG", inspect.currentframe())
    return True


@shared_task(name='online_plus_socket_renew')
@unpredicted_exception_handler("DEBUG")
def online_plus_socket_renew():
    from oracle.services.online_plus import LS_Class
    ls = LS_Class()
    ls.renew()
    return True


@shared_task(name='check_queue_condition')
@unpredicted_exception_handler("DEBUG")
def check_queue_condition():
    instruments = Instrument.get_instruments()
    for instrument in instruments:
        try:
            broadcast_instrument_queue_status(instrument)
        except Exception:
            exception_handler("DEBUG", inspect.currentframe())
    return True


@shared_task(name='check_order_balance')
@unpredicted_exception_handler("DEBUG")
def check_order_balance():
    instruments = Instrument.get_instruments()
    for instrument in instruments:
        try:
            broadcast_order_balance_status(instrument)
        except Exception:
            exception_handler("DEBUG", inspect.currentframe())
    return True


@shared_task(name='check_order_depth')
@unpredicted_exception_handler("DEBUG")
def check_order_depth():
    instruments = Instrument.get_instruments()
    for instrument in instruments:
        try:
            broadcast_order_depth_status(instrument)
        except Exception:
            exception_handler("DEBUG", inspect.currentframe())
    return True


@shared_task(name='check_recent_trades')
@unpredicted_exception_handler("DEBUG")
def check_recent_trades():
    instruments = Instrument.get_instruments()
    for instrument in instruments:
        try:
            broadcast_recent_trades_status(instrument)
        except Exception:
            exception_handler("DEBUG", inspect.currentframe())

    return True
