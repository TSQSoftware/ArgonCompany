from django.core.validators import FileExtensionValidator
from django.db import models


class TaskCategory(models.Model):
    name = models.CharField(max_length=100)
    icon = models.ImageField(
        upload_to="category_icons/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["jpg", "png", "jpeg"])],
    )
    duration_length_minutes = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Task categories"
        verbose_name = "Task category"

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=10)

    class Meta:
        verbose_name_plural = "Tags"
        verbose_name = "Tag"

    def __str__(self):
        return self.name
