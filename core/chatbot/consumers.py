from importlib.resources import path
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from chatbot.models import Conversation, Message
from domains.models import Website
from chatbot.utils import get_chat_group_name


class HumanChatConsumer(AsyncWebsocketConsumer):
    sender_type = "owner"  # default
    def __init__(self, *args, sender_type="owner", **kwargs):
        super().__init__(*args, **kwargs)
        self.sender_type = sender_type


    async def connect(self):
        self.widget_id = self.scope["url_route"]["kwargs"]["widget_id"]
        self.email = self.scope["url_route"]["kwargs"]["email"]
        self.sender = self.scope["url_route"]["kwargs"]["sender"]

        self.email = self.email.replace("%40", "@")

        self.room_group_name = get_chat_group_name(
            self.widget_id,
            self.email
        )

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()



    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message")
        

        if not message:
            return

        conversation = await self.get_conversation()

        await self.save_message(conversation, message, self.sender)



        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": self.sender,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"]
        }))

    # =========================
    # DATABASE
    # =========================

    @database_sync_to_async
    def get_conversation(self):
        website = Website.objects.get(widget_id=self.widget_id)

        conversation, _ = Conversation.objects.get_or_create(
            website=website,
            email=self.email
        )

        return conversation

    @database_sync_to_async
    def save_message(self, conversation, message, sender):
      Message.objects.create(
        conversation=conversation,
        sender=sender,
        text=message
    )

