from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def broadcast_trigger(data: dict):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(f"trigger",
                                            {"type": "send_data", "msg_type": "trigger", "data": data}, )
