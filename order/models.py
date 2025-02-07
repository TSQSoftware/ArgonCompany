from django.db import models

from worker.models import Worker


class OrderType(models.Model):
    name = models.CharField(max_length=100)


class Order(models.Model):
    name = models.CharField(max_length=100)
    type = models.ForeignKey(OrderType, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    contact_phone_number = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    workers = models.ManyToManyField(Worker, blank=True)