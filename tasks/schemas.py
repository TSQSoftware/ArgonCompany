from ninja import ModelSchema, Schema

from tasks.models import TaskType, Task
from worker.schemas import SimpleWorkerSchema


class TaskTypeSchema(ModelSchema):
    class Meta:
        model = TaskType
        fields = '__all__'


class TaskTypeCreateSchema(ModelSchema):
    class Meta:
        model = TaskType
        exclude = ('id',)


class TaskTypeUpdateSchema(Schema):
    name: str = None
    description: str = None


class TaskSchema(ModelSchema):
    task_type: dict | None
    workers: list[dict] | None = None

    @staticmethod
    def resolve_task_type(obj: Task) -> dict | None:
        if obj.type:
            return TaskTypeSchema.from_orm(obj.type).dict()
        return None

    @staticmethod
    def resolve_workers(obj: Task) -> list[dict] | None:
        workers = obj.workers.all()
        return [SimpleWorkerSchema.from_orm(worker).dict() for worker in workers] if workers else None

    class Meta:
        model = Task
        exclude = ('type',)


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
