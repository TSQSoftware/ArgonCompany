from ninja import ModelSchema, Schema

from client.schemas import ClientSchema
from data.schemas import TaskCategorySchema, TagSchema
from tasks.models import Task
from worker.schemas import SimpleWorkerSchema


class TaskTypeUpdateSchema(Schema):
    name: str = None
    description: str = None


class TaskSchema(ModelSchema):
    category: dict | None
    workers: list[dict] | None
    client: dict | None
    tags: list[dict] | None

    @staticmethod
    def resolve_category(obj: Task) -> dict | None:
        if obj.category:
            return TaskCategorySchema.from_orm(obj.category).dict()
        return None

    @staticmethod
    def resolve_client(obj: Task) -> dict | None:
        if obj.client:
            return ClientSchema.from_orm(obj.client).dict()
        return None

    @staticmethod
    def resolve_tags(obj: Task) -> list[dict] | None:
        tags = obj.tags.all()
        return [TagSchema.from_orm(tag).dict() for tag in tags] if tags else None

    @staticmethod
    def resolve_workers(obj: Task) -> list[dict] | None:
        workers = obj.workers.all()
        return [SimpleWorkerSchema.from_orm(worker).dict() for worker in workers] if workers else None

    class Meta:
        model = Task
        fields = '__all__'


class TaskCreateSchema(Schema):
    name: str
    type_id: int
    address: str
    contact_phone_number: str
    description: str


class TaskUpdateSchema(Schema):
    name: str = None
    type_id: int = None
    address: str = None
    contact_phone_number: str = None
    description: str = None
