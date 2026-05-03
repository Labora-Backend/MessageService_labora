import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Message


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]

        # 🔒 1. Check authentication
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return

        self.job_id = self.scope["url_route"]["kwargs"]["job_id"]
        self.room_group_name = f"chat_job_{self.job_id}"

        # 🔒 2. Check if user is allowed in this chat
        is_allowed = await self.is_user_allowed(self.user.id, self.job_id)

        if not is_allowed:
            await self.close()
            return

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

        content = data.get("content")
        receiver_id = data.get("receiver_id")

        if not content or not receiver_id:
            return

        # 🔒 Always take sender from authenticated user
        sender_id = self.user.id

        # 🔒 Optional: validate receiver belongs to this job chat
        is_allowed = await self.is_user_allowed(receiver_id, self.job_id)
        if not is_allowed:
            return "you are not allowed to use this method"

        message = await self.save_message(
            sender_id,
            receiver_id,
            content
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "id": message.id,
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "content": content,
                "created_at": message.created_at.isoformat(),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, content):
        return Message.objects.create(
            sender_id=sender_id,
            receiver_id=receiver_id,
            job_id=self.job_id,
            content=content
        )

    @database_sync_to_async
    def is_user_allowed(self, user_id, job_id):
        """
        🔥 IMPORTANT:
        Replace this with your actual logic:
        - Check if user is:
            ✔ job owner (client)
            ✔ OR accepted freelancer
        """

        # Example logic (you MUST replace with real models)
        from job.models import Job
        from message.models import Message

        # Check client
        if Job.objects.filter(id=job_id, client_id=user_id).exists():
            return True

        if Message.objects.filter(
            job_id=job_id,
            freelancer_id=user_id,
            status="accepted"
        ).exists():
            return True

        return False