from django.db import models
from location_field.forms.plain import PlainLocationField

from data.models import TaskCategory


class ClientMachineStatusType(models.TextChoices):
    ACTIVE = "active", "Active"
    UNDER_REPAIR = "under_repair", "Under Repair"
    DECOMMISSIONED = "decommissioned", "Decommissioned"


class ClientMachine(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(TaskCategory, on_delete=models.CASCADE, blank=True, null=True)
    client_place = models.ForeignKey("ClientPlace", on_delete=models.SET_NULL, related_name="machines", null=True,
                                     blank=True)
    identifier = models.PositiveIntegerField(blank=True, null=True)
    serial_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    status = models.CharField(max_length=20, choices=ClientMachineStatusType.choices,
                              default=ClientMachineStatusType.ACTIVE)
    purchase_date = models.DateField(blank=True, null=True)
    last_service_date = models.DateField(blank=True, null=True)
    next_service_date = models.DateField(blank=True, null=True)
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    warranty_expiry = models.DateField(blank=True, null=True)
    location_notes = models.TextField(blank=True, null=True)
    operating_hours = models.PositiveIntegerField(blank=True, null=True)
    power_supply = models.CharField(max_length=50, blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    dimensions = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to="machines/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Client machine"
        verbose_name_plural = "Client machines"
        unique_together = ("client_place", "identifier")

    def save(self, *args, **kwargs):
        """ Automatically assign an incrementing identifier per ClientPlace. """
        if self.identifier is None:
            last_machine = ClientMachine.objects.filter(client_place=self.client_place).order_by("identifier").last()
            self.identifier = 1 if last_machine is None else last_machine.identifier + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client_place.name if self.client_place else 'No Place'} - {self.name} (#{self.identifier})"


class ClientPlaceType(models.TextChoices):
    WAREHOUSE = "warehouse", "Warehouse"
    OFFICE = "office", "Office"
    FACTORY = "factory", "Factory"
    STORE = "store", "Store"
    OTHER = "other", "Other"


class ClientPlace(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    place_type = models.CharField(max_length=50, choices=ClientPlaceType.choices, blank=True, null=True)
    location = PlainLocationField(based_fields=['latitude', 'longitude'], zoom=7, null=True, blank=True)
    operating_hours = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Client place"
        verbose_name_plural = "Client places"

    def __str__(self):
        return self.name


class ClientStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    PROSPECTIVE = "prospective", "Prospective"


class Client(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    nip_number = models.CharField(max_length=100, blank=True, null=True)
    regon_number = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50, choices=ClientStatus.choices, default=ClientStatus.ACTIVE)
    client_places = models.ManyToManyField(ClientPlace, related_name="places", blank=True)
    notes = models.TextField(blank=True, null=True)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def __str__(self):
        return f"{self.name} ({self.short_name})" if self.short_name else self.name
