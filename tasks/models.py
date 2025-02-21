from django.db import models
from geopy import Nominatim
from geopy.exc import GeocoderTimedOut
from location_field.models.plain import PlainLocationField

from client.models import Client, ClientObject, ClientMachine
from data.models import Tag, TaskCategory
from worker.models import Worker


class TaskStatus(models.TextChoices):
    IN_PROGRESS = 'in_progress', 'In progress'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'
    NOT_STARTED = 'not_started', 'Not started'
    AWAITING_CONFIRMATION = 'awaiting_confirmation', 'Awaiting confirmation'


class Task(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(TaskCategory, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    contact_phone_number = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    workers = models.ManyToManyField(Worker, blank=True)
    location = PlainLocationField(based_fields=['latitude', 'longitude'], zoom=7, null=True, blank=True)
    status = models.CharField(choices=TaskStatus.choices, default=TaskStatus.NOT_STARTED, max_length=50)
    expected_realization_duration = models.DurationField(null=True, blank=True)
    expected_realization_date = models.DateField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='related_clients')
    client_objects = models.ManyToManyField(ClientObject, blank=True, related_name='related_client_objects')
    client_machines = models.ManyToManyField(ClientMachine, blank=True, related_name='related_client_machines')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.category.name if self.category else ''} | {self.name} [{self.workers.count()} workers]"

    def get_location(self) -> str | None:
        if self.location is None:
            return None

        if isinstance(self.location, str):
            try:
                lat, lon = map(float, self.location.split(','))
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
