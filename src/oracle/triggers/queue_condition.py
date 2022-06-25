def broadcast_instrument_queue_status(instrument):
    from morpheus.services.broadcast import broadcast_trigger
    from oracle.data_type.instrument_market_data import InstrumentData
    from oracle.utils import check_instrument_queue_status


    queue_condition = check_instrument_queue_status(instrument)
    instrument_state = {"queue": queue_condition}
    InstrumentData.update(instrument.isin, "state", instrument_state)
    if queue_condition:
        broadcast_trigger(isin=instrument.isin, data={"trigger_type": "queue_condition", "queue_side": queue_condition})
