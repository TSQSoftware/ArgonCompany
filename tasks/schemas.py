from ninja import ModelSchema

from client.schemas import ClientSchema, ClientPlaceSchema, ClientMachineSchema
from data.schemas import TaskCategorySchema, TagSchema
from tasks.models import Task, TaskNote, TaskAttachment, TaskStatus
from worker.schemas import SimpleWorkerSchema


class TaskNoteSchema(ModelSchema):
    worker: dict | None

    @staticmethod
    def resolve_worker(obj: TaskNote) -> dict | None:
        if obj.worker is None:
            return None
        return SimpleWorkerSchema.from_orm(obj.worker).dict()

    class Meta:
        model = TaskNote
        fields = '__all__'


class TaskAttachmentSchema(ModelSchema):
    worker: dict | None

    @staticmethod
    def resolve_worker(obj: TaskNote) -> dict | None:
        if obj.worker is None:
            return None
        return SimpleWorkerSchema.from_orm(obj.worker).dict()

    class Meta:
        model = TaskAttachment
        fields = '__all__'


class TaskStatusSchema(ModelSchema):
    color: str | None

    @staticmethod
    def resolve_color(obj: TaskStatus) -> str | None:
        if obj.color:
            return obj.color.color
        return None


    class Meta:
        model = TaskStatus
        fields = '__all__'


class TaskSchema(ModelSchema):
    category: dict | None
    workers: list[dict]
    client: dict | None
    tags: list[dict]
    client_places: list[dict]
    client_machines: list[dict]
    notes: list[dict]
    attachments: list[dict]
    status: dict | None

    @staticmethod
    def resolve_status(obj: Task) -> dict | None:
        if obj.status:
            return TaskStatusSchema.from_orm(obj.status).dict()
        return None

    @staticmethod
    def resolve_notes(obj: Task) -> list[dict]:
        notes = obj.notes.all()
        return [TaskNoteSchema.from_orm(note).dict() for note in notes] if notes else []

    @staticmethod
    def resolve_attachments(obj: Task) -> list[dict]:
        attachments = obj.attachments.all()
        return [TaskAttachmentSchema.from_orm(attachment).dict() for attachment in attachments] if attachments else []

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
    def resolve_tags(obj: Task) -> list[dict]:
        tags = obj.tags.all()
        return [TagSchema.from_orm(tag).dict() for tag in tags] if tags else []

    @staticmethod
    def resolve_client_places(obj: Task) -> list[dict]:
        client_places = obj.client_places.all()
        return [ClientPlaceSchema.from_orm(client_place).dict() for client_place in
                client_places] if client_places else []

    @staticmethod
    def resolve_client_machines(obj: Task) -> list[dict]:
        client_machines = obj.client_machines.all()
        return [ClientMachineSchema.from_orm(client_machine).dict() for client_machine in
                client_machines] if client_machines else []

    @staticmethod
    def resolve_workers(obj: Task) -> list[dict]:
        workers = obj.workers.all()
        return [SimpleWorkerSchema.from_orm(worker).dict() for worker in workers] if workers else []

    class Meta:
        model = Task
        fields = '__all__'
