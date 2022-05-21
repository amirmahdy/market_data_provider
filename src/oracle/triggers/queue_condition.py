def check_instrument_queue_status(instrument):
    from oracle.data_type.instrument_market_data import InstrumentData
    from oracle.services.tsetmc_market import get_tse_instrument_data

    market_data = InstrumentData.get(ref_group='market', isin=instrument.isin)
    if market_data is None:
        market_data = get_tse_instrument_data(instrument)
    if market_data['high_allowed_price'] == market_data['bid_ask_first_row']['best_buy_price']:
        return 'buy'
    if market_data['low_allowed_price'] == market_data['bid_ask_first_row']['best_sell_price']:
        return 'sell'


def broadcast_instrument_queue_status(instrument):
    from morpheus.services.broadcast import broadcast_trigger
    broadcast_trigger(
            isin=instrument.isin, data={'trigger_type': 'queue_condition', 'queue_side': check_instrument_queue_status(instrument)})
