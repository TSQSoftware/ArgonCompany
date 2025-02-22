from django.db import models

from data.models import TaskCategory


class ClientMachine(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(TaskCategory, on_delete=models.CASCADE, blank=True, null=True)
    client_place = models.ForeignKey("ClientPlace", on_delete=models.SET_NULL, related_name="machines", null=True, blank=True)
    identifier = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Client machine"
        verbose_name_plural = "Client machines"
        unique_together = ("client_place", "identifier")

    def save(self, *args, **kwargs):
        """ Automatically set `identifier` if not provided. """
        if self.identifier is None:
            last_machine = ClientMachine.objects.filter(client_place=self.client_place).order_by("identifier").last()
            self.identifier = 1 if last_machine is None else last_machine.identifier + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client_place.name} - {self.name} (#{self.identifier})"


class ClientPlace(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Client place"
        verbose_name_plural = "Client places"

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
    client_places = models.ManyToManyField(ClientPlace, related_name='places', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def __str__(self):
        return self.name
