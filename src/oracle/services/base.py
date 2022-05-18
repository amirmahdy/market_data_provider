from oracle.services.tsetmc_market import get_tse_instrument_data
from oracle.services.tsetmc_askbid import get_live_askbid
from oracle.services.tsetmc_indices import get_indices_live
from oracle.data_type.instrument_market_data import InstrumentData
from oracle.services.tsetmc_indinst import get_live_indinst


def initial_setup():
    from oracle.models import Instrument
    instruments = Instrument.get_instruments()
    for instrument in instruments:
        instrument_data = get_tse_instrument_data(instrument)
        instrument_askbid = get_live_askbid(instrument.tse_id)
        instrument_indinst = get_live_indinst(instrument.tse_id, instrument.isin)

        InstrumentData.update(instrument.isin, 'market', instrument_data)
        InstrumentData.update(instrument.isin, 'askbid', instrument_askbid)
        InstrumentData.update(instrument.isin, 'indinst', instrument_indinst)

    instrument_indices = get_indices_live()
    for index in instrument_indices:
        InstrumentData.update(index['symbol_isin'], 'index', index)


