from celery import shared_task
from oracle.services.tsetmc_market_data import get_tse_instrument_data
from oracle.models import Instrument
from oracle.data_type.instrument_market_data import Instrument_Maker_Data
from oracle.cache.base import Cache

cache = Cache()


@shared_task(name="tsetmc_market_data_update")
def market_data_update():
    try:
        instruments = Instrument.get_instruments()
        for instrument in instruments:
            res = get_tse_instrument_data(instrument.tse_id)
            Instrument_Maker_Data.update(instrument.isin, res)
    except Exception as e:
        print(e)
        return e
    return True
