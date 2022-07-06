def broadcast_order_depth_status(instrument):
    from morpheus.services.broadcast import broadcast_trigger
    from oracle.utils import check_buy_order_depth_status, check_sell_order_depth_status
    from oracle.data_type.instrument_market_data import InstrumentData


    buy_order_depth = check_buy_order_depth_status(instrument)
    sell_order_depth = check_sell_order_depth_status(instrument)
    instrument_state = InstrumentData.get(instrument.isin, "state")
    instrument_state["buy_order_depth"] = buy_order_depth
    instrument_state["sell_order_depth"] = sell_order_depth
    InstrumentData.update(instrument.isin, "state", instrument_state)
    broadcast_trigger(isin=instrument.isin, data={"trigger_type": "buy_order_depth", "order_depth": buy_order_depth})
    broadcast_trigger(isin=instrument.isin, data={"trigger_type": "sell_order_depth", "order_depth": sell_order_depth})
