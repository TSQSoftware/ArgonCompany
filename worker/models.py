import uuid

from django.db import models
from location_field.models.plain import PlainLocationField

from data.models import UserRole


def get_default_user_role():
    """Returns the user role with the lowest permission level"""
    return UserRole.objects.first()


class Worker(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    activation_key = models.CharField(max_length=36, null=True, blank=True)
    uuid = models.UUIDField(null=True, blank=True)
    role = models.ForeignKey(UserRole, on_delete=models.SET_DEFAULT, default=get_default_user_role)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def set_random_activation_key(self) -> str:
        self.activation_key = str(uuid.uuid4())
        self.save()
        return self.activation_key


class WorkerLocation(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField()
    altitude = models.FloatField(blank=True, null=True)
    speed = models.FloatField(blank=True, null=True)
    location = PlainLocationField(based_fields=['latitude', 'longitude'], zoom=7)

    def __str__(self):
        return f"{self.timestamp} {self.altitude} {self.speed} {self.location}"
