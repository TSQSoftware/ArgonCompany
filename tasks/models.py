import os
from datetime import datetime

from django.db import models
from geopy import Nominatim
from geopy.exc import GeocoderTimedOut
from location_field.models.plain import PlainLocationField

from client.models import Client, ClientPlace, ClientMachine
from data.models import Tag, TaskCategory, Color
from worker.models import Worker


class TaskStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)
    require_confirmation = models.BooleanField(default=False)
    color = models.ForeignKey(Color, null=True, blank=True, default=Color.default, on_delete=models.SET_NULL)
    completed = models.BooleanField(default=False)

    class Config:
        arbitrary_types_allowed = True

    def __str__(self):
        return self.name


class Task(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(TaskCategory, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    contact_phone_number = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    workers = models.ManyToManyField(Worker, blank=True)
    location = PlainLocationField(based_fields=['latitude', 'longitude'], zoom=7, null=True, blank=True)
    status = models.ForeignKey(TaskStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
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
                    location = geolocator.reverse((lat, lon), language='pl', timeout=10)
                    return location.address if location else None
                except GeocoderTimedOut:
                    return None
                except Exception:
                    return None
            except ValueError:
                return None

    def get_contact_info(self):
        return self.contact_phone_number or None


class TaskNote(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='notes')
    note = models.TextField()
    worker = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    custom_id = models.CharField(max_length=50, unique=True, blank=True, null=True)

    class Meta:
        verbose_name = "Task Note"
        verbose_name_plural = "Task Notes"
        ordering = ['-created_at']

    def __str__(self):
        name = f'{self.worker.first_name} {self.worker.last_name}' if self.worker else 'Unknown'
        return f"Note [{self.custom_id}] for Task: {self.task.name} by {name}"

    def save(self, *args, **kwargs):
        if not self.custom_id:
            current_year = (self.created_at if self.created_at else datetime.now()).year
            notes_count = self.task.notes.count() + 1
            custom_id = f"{notes_count}/{self.task.id}/{current_year}"

            while self.__class__.objects.filter(custom_id=custom_id).exists():
                notes_count += 1
                custom_id = f"{notes_count}/{self.task.id}/{current_year}"

            self.custom_id = custom_id

        super().save(*args, **kwargs)


def task_attachment_upload_path(instance, filename):
    return os.path.join('task_attachments', str(instance.id), filename)


def task_image_upload_path(instance, filename):
    return os.path.join('task_images', str(instance.id), filename)

class AttachmentType(models.TextChoices):
    CLIENT_SIGNATURE = "client_signature", "Client Signature"
    WORKER_SIGNATURE = "worker_signature", "Worker Signature"

class TaskAttachment(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='attachments')
    worker = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='task_attachments')
    file = models.FileField(upload_to=task_attachment_upload_path, blank=True, null=True)
    image = models.ImageField(upload_to=task_image_upload_path, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    attachment_type = models.CharField(
        max_length=20,
        choices=[('image', 'Image'), ('file', 'File')],
        default='file'
    )
    custom_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    type = models.CharField(max_length=50, choices=AttachmentType.choices, blank=True, null=True)

    class Meta:
        verbose_name = "Task Attachment"
        verbose_name_plural = "Task Attachments"

    def __str__(self):
        return f"Attachment {self.custom_id} for Task {self.task.id}"

    def save(self, *args, **kwargs):
        if not self.custom_id:
            current_year = (self.created_at if self.created_at else datetime.now()).year
            attachment_count = self.task.attachments.count() + 1
            custom_id = f"{attachment_count}/{self.task.id}/{current_year}"

            while self.__class__.objects.filter(custom_id=custom_id).exists():
                attachment_count += 1
                custom_id = f"{attachment_count}/{self.task.id}/{current_year}"

            self.custom_id = custom_id

        super().save(*args, **kwargs)
