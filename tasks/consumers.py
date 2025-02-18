import json
from datetime import datetime, date

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from tasks.models import Task
from tasks.schemas import TaskSchema


class TasksConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.worker_id = None
        self.group_name = None

    async def connect(self):
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)

        if data.get("action") == "get_tasks":
            self.worker_id = data.get("worker_id")
            if self.worker_id:
                # Subscribe to task updates for the worker
                self.group_name = f'task_updates_{self.worker_id}'
                await self.channel_layer.group_add(self.group_name, self.channel_name)
                await self.send(
                    text_data=json.dumps({"message": f"Subscribed to task updates for worker {self.worker_id}"}, default=TasksConsumer.date_serializer))

                # Get tasks for the worker and send them
                tasks = await self.get_tasks(self.worker_id)
                await self.send(text_data=json.dumps({"tasks": tasks}, default=TasksConsumer.date_serializer))

    async def disconnect(self, close_code):
        if self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        print("Worker disconnected")

    @sync_to_async
    def get_tasks(self, worker_id: int) -> list[dict]:
        tasks = Task.objects.filter(workers__in=[worker_id])
        return [TaskSchema.from_orm(task).dict() for task in tasks]

    async def task_update(self, event):
        tasks = await self.get_tasks(self.worker_id)
        await self.send(text_data=json.dumps({"tasks": tasks}, default=TasksConsumer.date_serializer))

    @staticmethod
    def date_serializer(obj):
        """
        Serialize datetime and date objects into ISO 8601 format.
        """
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError(f"Type {obj.__class__.__name__} not serializable")
