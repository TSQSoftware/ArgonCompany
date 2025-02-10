from ninja import ModelSchema, Schema

from tasks.models import TaskType, Task


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
