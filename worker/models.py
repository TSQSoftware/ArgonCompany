import uuid

from django.db import models

class WorkerRole(models.TextChoices):
    WORKER = "worker", "Worker"
    MOD = "mod", "Moderator"
    ADMIN = "data", "Administrator"

class Worker(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    activation_key = models.CharField(max_length=36, null=True, blank=True)
    uuid = models.UUIDField(null=True, blank=True)
    role = models.CharField(max_length=50, choices=WorkerRole.choices, default=WorkerRole.WORKER)

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
    longitude = models.FloatField()
    latitude = models.FloatField()

    def __str__(self):
        return f"{self.timestamp} {self.altitude} {self.speed} {self.longitude} {self.latitude}"