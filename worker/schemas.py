from datetime import date
from typing import Optional

from ninja import ModelSchema, Schema

from worker.models import Worker, WorkerRole


class WorkerSchema(ModelSchema):
    class Meta:
        model = Worker
        fields = '__all__'


class WorkerCreateSchema(Schema):
    first_name: str
    last_name: str
    date_of_birth: Optional[date] = None
    phone_number: Optional[str] = None
    role: Optional[WorkerRole] = None

class WorkerUpdateSchema(Schema):
    first_name: str = None
    last_name: str = None
    date_of_birth: Optional[date] = None
    phone_number: Optional[str] = None
    role: Optional[WorkerRole] = None
