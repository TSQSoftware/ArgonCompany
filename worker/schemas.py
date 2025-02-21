from datetime import date, datetime
from typing import Optional

from ninja import ModelSchema, Schema

from argon_company import settings
from worker.models import Worker, WorkerRole, WorkerLocation


class WorkerSchema(ModelSchema):
    class Meta:
        model = Worker
        fields = '__all__'


class CompanyWorkerSchema(ModelSchema):
    company_name: str

    @staticmethod
    def resolve_company_name(obj: Worker) -> str:
        return settings.COMPANY_NAME

    class Meta:
        model = Worker
        fields = '__all__'


class SimpleWorkerSchema(ModelSchema):
    class Meta:
        model = Worker
        exclude = ('date_of_birth', 'phone_number', 'is_active', 'activation_key', 'uuid')


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

class WorkerLocationSchema(ModelSchema):
    class Meta:
        model = WorkerLocation
        fields = '__all__'

class WorkerLocationCreateSchema(Schema):
    timestamp: datetime
    altitude: float
    speed: float
    longitude: float
    latitude: float