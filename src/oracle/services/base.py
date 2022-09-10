from oracle.services.tsetmc_market import get_tse_instrument_data
from oracle.services.tsetmc_askbid import get_live_askbid
from oracle.services.tsetmc_indices import get_indices_live
from oracle.data_type.instrument_market_data import InstrumentData
from oracle.services.tsetmc_indinst import get_live_indinst
from oracle.services.tsetmc_trades import get_trades
from oracle.utils import (
    check_instrument_queue_status,
    check_order_balance_status,
    check_buy_order_depth_status,
    check_sell_order_depth_status,
    check_recent_trades_status,
)
from oracle.utils import check_instrument_queue_status
from oracle.data_type.heart_beat import HeartBeat
from mdp.exception_handler import unpredicted_exception_handler


@unpredicted_exception_handler("DEBUG")
def initial_setup():
    from oracle.models import Instrument
    instruments = Instrument.get_instruments()
    source = "TSETMC"
    for instrument in instruments:
        instrument_data = get_tse_instrument_data(instrument)
        instrument_askbid = get_live_askbid(instrument.tse_id)
        instrument_indinst = get_live_indinst(instrument.tse_id, instrument.isin)
        instrument_trades = get_trades(instrument.tse_id)

        InstrumentData.update(instrument.isin, 'market', instrument_data)
        HeartBeat.update(source, 'market')
        InstrumentData.update(instrument.isin, 'askbid', instrument_askbid)
        HeartBeat.update(source, 'askbid')
        InstrumentData.update(instrument.isin, 'indinst', instrument_indinst)
        HeartBeat.update(source, 'indinst')
        InstrumentData.update(instrument.isin, 'trades', instrument_trades)
        HeartBeat.update(source, 'trades')

        instrument_state = {
            'state': instrument_data['market_status'],
            'queue': check_instrument_queue_status(instrument),
            'order_balance': check_order_balance_status(instrument),
            'buy_order_depth': check_buy_order_depth_status(instrument),
            'sell_order_depth': check_sell_order_depth_status(instrument),
            'recent_trades': check_recent_trades_status(instrument),
        }
        InstrumentData.update(instrument.isin, 'state', instrument_state)
        HeartBeat.update(source, 'state')

    instrument_indices = get_indices_live()
    for index in instrument_indices:
        InstrumentData.update(index['SymbolISIN'], 'index', index)
        HeartBeat.update(source, 'index')
