from django.db import models

from data.models import TaskCategory


class ClientMachine(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(TaskCategory, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ClientObject(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    machines = models.ManyToManyField(ClientMachine, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    nip_number = models.CharField(max_length=100, blank=True, null=True)
    regon_number = models.CharField(max_length=100, blank=True, null=True)
    client_objects = models.ManyToManyField(ClientObject, related_name='objects', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
