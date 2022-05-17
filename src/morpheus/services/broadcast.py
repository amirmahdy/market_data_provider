from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def broadcast_trigger(isin: str, data: dict):
    channel_layer = get_channel_layer()
    data = {"isin": isin, "data": data}
    async_to_sync(channel_layer.group_send)(f"trigger_{isin}",
                                            {"type": "send_data", "msg_type": "trigger", "data": data}, )


def broadcast_market_data(isin: str, market_data):
    channel_layer = get_channel_layer()
    data = {"isin": isin, "data": market_data}
    async_to_sync(channel_layer.group_send)(f"market_{isin}", {
        "type": "send_data", "msg_type": "market_data", "data": data})


def broadcast_askbid_data(isin: str, askbid_data):
    channel_layer = get_channel_layer()
    data = {"isin": isin, "data": askbid_data}
    async_to_sync(channel_layer.group_send)(f"askbid_{isin}", {
        "type": "send_data", "msg_type": "askbid_data", "data": data})


def broadcast_indices_data(index_data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(f"index", {
        "type": "send_data", "msg_type": "index_data", "data": index_data})


def broadcast_indinst_data(isin: str, indinst_data):
    channel_layer = get_channel_layer()
    data = {"isin": isin, "data": indinst_data}
    async_to_sync(channel_layer.group_send)(f"indinst_{isin}", {
        "type": "send_data", "msg_type": "indinst_data", "data": data})
