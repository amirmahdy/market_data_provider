def broadcast_recent_trades_status(instrument):
    from morpheus.services.broadcast import broadcast_trigger
    from oracle.utils import check_recent_trades_status


    recent_trades = check_recent_trades_status(instrument)

    broadcast_trigger(isin=instrument.isin, data={"trigger_type": "recent_trades", "recent_trades": recent_trades})
