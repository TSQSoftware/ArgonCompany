from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim
from ninja import ModelSchema, Schema

from data.schemas import TaskCategorySchema
from tasks.models import Task
from worker.schemas import SimpleWorkerSchema

class TaskTypeUpdateSchema(Schema):
    name: str = None
    description: str = None


class TaskSchema(ModelSchema):
    task_type: dict | None
    workers: list[dict] | None = None
    task_location: str | None

    @staticmethod
    def resolve_task_type(obj: Task) -> dict | None:
        if obj.category:
            return TaskCategorySchema.from_orm(obj.category).dict()
        return None

    @staticmethod
    def resolve_workers(obj: Task) -> list[dict] | None:
        workers = obj.workers.all()
        return [SimpleWorkerSchema.from_orm(worker).dict() for worker in workers] if workers else None

    @staticmethod
    def resolve_task_location(obj: Task) -> str | None:
        return None

        if obj.location is None:
            return None

        if isinstance(obj.location, str):
            try:
                lat, lon = map(float, obj.location.split(','))
                geolocator = Nominatim(user_agent="myGeocoder")

                try:
                    location = geolocator.reverse((lat, lon), language='pl', timeout=1)
                    return location.address if location else None
                except GeocoderTimedOut:
                    return None
                except Exception:
                    return None

            except ValueError:
                return None

        return None

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
