from channels.generic.websocket import AsyncJsonWebsocketConsumer


class MDPConsumer(AsyncJsonWebsocketConsumer):
    groups = set()

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        for group in self.groups:
            await self.channel_layer.group_discard(group, self.channel_name)

    async def receive_json(self, content):
        try:
            if content["type"] == "subscribe":
                await self.handle_subscription(content)
            elif content["type"] == "unsubscribe":
                await self.handle_unsubscription(content)
        except Exception as e:
            print(e)
            await self.send_json(
                {
                    "status": "failure",
                    "message": "Could not parse request or an error has occurred.",
                }
            )

    async def send_data(self, event):
        await self.send_json({"msg_type": event['msg_type'], "data": event['data']})

    async def add_to_group(self, group_name: str):
        await self.channel_layer.group_add(group_name, self.channel_name)
        self.groups.add(group_name)

    async def remove_from_group(self, group_name: str):
        await self.channel_layer.group_discard(group_name, self.channel_name)
        self.groups.remove(group_name)

    async def subscribe_to_topic(self, topic_name):
        await self.add_to_group(topic_name)
        await self.send_json(
            {
                "status": "ok",
                "topic": topic_name,
                "type": "subscription_result",
            }
        )

    async def unsubscribe_to_topic(self, topic_name):
        await self.remove_from_group(topic_name)
        await self.send_json(
            {
                "status": "ok",
                "topic": topic_name,
                "type": "unsubscription_result",
            }
        )

    async def handle_subscription(self, request):
        if request["topic"] == "trigger":
            isins = request["isins"]
            for isin in isins:
                await self.subscribe_to_topic(f"trigger_{isin}")
        elif request["topic"] == "market":
            isins = request["isins"]
            for isin in isins:
                await self.subscribe_to_topic(f"market_{isin}")
        elif request["topic"] == "askbid":
            isins = request["isins"]
            for isin in isins:
                await self.subscribe_to_topic(f"askbid_{isin}")
        elif request["topic"] == "index":
            await self.subscribe_to_topic(f"index")

    async def handle_unsubscription(self, request):
        if request["topic"] == "trigger":
            isins = request["isins"]
            for isin in isins:
                await self.unsubscribe_to_topic(f"trigger_{isin}")
        elif request["topic"] == "market":
            isins = request["isins"]
            for isin in isins:
                await self.unsubscribe_to_topic(f"market_{isin}")
        elif request["topic"] == "askbid":
            isins = request["isins"]
            for isin in isins:
                await self.unsubscribe_to_topic(f"askbid_{isin}")
        elif request["topic"] == "index":
            await self.unsubscribe_to_topic(f"index")
