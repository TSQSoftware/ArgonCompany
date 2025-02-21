import json
from datetime import datetime, date, timedelta

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
                    text_data=json.dumps({"message": f"Subscribed to task updates for worker {self.worker_id}"},
                                         default=TasksConsumer.date_serializer))

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
        Serialize datetime, date, and timedelta objects into a JSON-serializable format.
        - datetime/date: ISO 8601 format (e.g., "2024-02-21T15:30:00")
        - timedelta: ISO 8601 duration format (e.g., "P3DT04H15M30S" for 3 days, 4 hours, 15 minutes, 30 seconds)
        """
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, timedelta):
            total_seconds = int(obj.total_seconds())
            days, remainder = divmod(total_seconds, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f'P{days}DT{hours:02}H{minutes:02}M{seconds:02}S'
        raise TypeError(f"Type {obj.__class__.__name__} not serializable")
