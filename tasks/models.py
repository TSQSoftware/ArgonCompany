from django.db import models
from location_field.models.plain import PlainLocationField

from worker.models import Worker


class TaskType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class TaskStatus(models.TextChoices):
    IN_PROGRESS = 'in_progress', 'In progress'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'
    NOT_STARTED = 'not_started', 'Not started'

class Task(models.Model):
    name = models.CharField(max_length=100)
    type = models.ForeignKey(TaskType, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    contact_phone_number = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    workers = models.ManyToManyField(Worker, blank=True)
    location = PlainLocationField(based_fields=['latitude', 'longitude'], zoom=7, null=True, blank=True)
    status = models.CharField(choices=TaskStatus.choices, default=TaskStatus.NOT_STARTED, max_length=50)

    def __str__(self):
        return f"{self.type.name if self.type else ''} | {self.name} [{self.workers.count()} workers]"
