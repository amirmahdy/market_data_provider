from celery import shared_task
from oracle.services.tsetmc_market_data import get_tse_instrument_data
from oracle.models import Instrument
from oracle.data_type.instrument_market_data import InstrumentData
from oracle.cache.base import Cache
from oracle.services.today_trades_history import get_trades

cache = Cache()


@shared_task(name="tsetmc_market_data_update")
def market_data_update():
    try:
        instruments = Instrument.get_instruments()
        for instrument in instruments:
            res = get_tse_instrument_data(instrument.tse_id)
            InstrumentData.update(instrument.isin, "market", res)
    except Exception as e:
        print(e)
        return e
    return True


### TODO modify this func to pass yesterday date as desired format
### @hatef

@shared_task(name="tsetmc_trade_data_update")
def trade_data_yesterday_update():
    try:
        instruments = Instrument.get_instruments()
        for instrument in instruments:
            today_trades = get_trades(instrument.tse_id)
            InstrumentData.update(instrument.isin, 'today_trades', today_trades)
    except Exception as e:
        print(e)
        return e
    return True


@shared_task(name="tsetmc_trade_data_update")
def trade_data_today_update():
    try:
        instruments = Instrument.get_instruments()
        for instrument in instruments:
            today_trades = get_trades(instrument.tse_id)
            InstrumentData.update(instrument.isin, 'today_trades', today_trades)
    except Exception as e:
        print(e)
        return e
    return True
