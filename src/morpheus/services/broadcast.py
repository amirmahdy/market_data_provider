from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def broadcast_trigger(data: dict):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(f"trigger",
                                            {"type": "send_data", "msg_type": "trigger", "data": data}, )


def broadcast_market_data(isin: str, market_data: dict):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(f"market", {
        "type": "send_data", "msg_type": "market_data", "data": {"isin": isin, "market_data": market_data}})
