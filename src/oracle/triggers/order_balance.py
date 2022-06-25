def broadcast_order_balance_status(instrument):
    from morpheus.services.broadcast import broadcast_trigger
    from oracle.data_type.instrument_market_data import InstrumentData
    from oracle.utils import check_order_balance_status


    order_balance = check_order_balance_status(instrument)

    broadcast_trigger(isin=instrument.isin, data={"trigger_type": "order_balance", "order_balance": order_balance})
