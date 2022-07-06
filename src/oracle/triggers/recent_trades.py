def broadcast_recent_trades_status(instrument):
    from morpheus.services.broadcast import broadcast_trigger
    from oracle.utils import check_recent_trades_status
    from oracle.data_type.instrument_market_data import InstrumentData

    recent_trades = check_recent_trades_status(instrument)
    instrument_state = InstrumentData.get(instrument.isin, 'state')
    instrument_state["recent_trades"] = recent_trades
    InstrumentData.update(instrument.isin, "state", instrument_state)

    broadcast_trigger(isin=instrument.isin, data={"trigger_type": "recent_trades", "recent_trades": recent_trades})
