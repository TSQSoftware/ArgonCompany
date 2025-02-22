from datetime import datetime

from django.db import models
from geopy import Nominatim
from geopy.exc import GeocoderTimedOut
from location_field.models.plain import PlainLocationField

from client.models import Client, ClientPlace, ClientMachine
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
    client_places = models.ManyToManyField(ClientPlace, blank=True, related_name='related_client_places')
    client_machines = models.ManyToManyField(ClientMachine, blank=True, related_name='related_client_machines')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)

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


class TaskNote(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='notes')
    note = models.TextField()
    created_by = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    custom_id = models.CharField(max_length=50, unique=True, blank=True, null=True)

    class Meta:
        verbose_name = "Task Note"
        verbose_name_plural = "Task Notes"
        ordering = ['-created_at']

    def __str__(self):
        name = f'{self.created_by.first_name} {self.created_by.last_name}' if self.created_by else 'Unknown'
        return f"Note [{self.custom_id}] for Task: {self.task.name} by {name}"

    def save(self, *args, **kwargs):
        if not self.custom_id:
            current_year = (self.created_at if self.created_at else datetime.now()).year
            notes_count = self.task.notes.count() + 1
            custom_id = f"/{notes_count}/{self.task.id}/{current_year}"

            while self.__class__.objects.filter(custom_id=custom_id).exists():
                notes_count += 1
                custom_id = f"{notes_count}/{self.task.id}/{current_year}"

            self.custom_id = custom_id

        super().save(*args, **kwargs)


class TaskAttachment(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='attachments')
    worker = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='task_attachments')
    file = models.FileField(upload_to='task_attachments/', blank=True, null=True)
    image = models.ImageField(upload_to='task_images/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    attachment_type = models.CharField(
        max_length=20,
        choices=[('image', 'Image'), ('file', 'File')],
        default='file'
    )
    custom_id = models.CharField(max_length=50, unique=True, blank=True, null=True)

    class Meta:
        verbose_name = "Task Attachment"
        verbose_name_plural = "Task Attachments"

    def __str__(self):
        return f"Attachment {self.custom_id} for Task {self.task.id}"

    def save(self, *args, **kwargs):
        if not self.custom_id:
            current_year = (self.created_at if self.created_at else datetime.now()).year
            attachment_count = self.task.attachments.count() + 1
            custom_id = f"/{attachment_count}/{self.task.id}/{current_year}"

            while self.__class__.objects.filter(custom_id=custom_id).exists():
                attachment_count += 1
                custom_id = f"{attachment_count}/{self.task.id}/{current_year}"

            self.custom_id = custom_id

        super().save(*args, **kwargs)
