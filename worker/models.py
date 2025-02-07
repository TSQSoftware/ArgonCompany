from django.db import models

class WorkerRole(models.TextChoices):
    WORKER = "worker", "Worker"
    MOD = "mod", "Moderator"
    ADMIN = "admin", "Administrator"

class Worker(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    uuid = models.UUIDField(null=True, blank=True)
    role = models.CharField(max_length=50, choices=WorkerRole.choices, default=WorkerRole.WORKER)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
