from django.db import models

from data.models import TaskCategory


class ClientMachine(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(TaskCategory, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ClientObject(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    machines = models.ManyToManyField(ClientMachine)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    nip_number = models.CharField(max_length=100, blank=True, null=True)
    regon_number = models.CharField(max_length=100, blank=True, null=True)
    objects = models.ManyToManyField(ClientObject, related_name='objects', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
