from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def broadcast_trigger(isin: str, data: dict):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(f"trigger_{isin}",
                                            {"type": "send_data", "msg_type": "trigger", "data": data}, )


def broadcast_market_data(isin: str, market_data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(f"market_{isin}", {
        "type": "send_data", "msg_type": "market_data", "data": market_data})

def broadcast_askbid_data(isin:str, askbid_data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(f"askbid_{isin}", {
        "type": "send_data", "msg_type": "askbid_data", "data": askbid_data})