from django.core.validators import FileExtensionValidator
from django.db import models


class UserRoleFeature(models.TextChoices):
    CHANGE_BASIC_TASK_STATUS = "change_basic_task_status", "Change basic task status"
    CHANGE_ALL_TASK_STATUS = "change_all_task_status", "Change all task status"
    DELETE_TASK = "delete_task", "Delete Task"
    EDIT_TASK = "edit_task", "Edit Task"


class Feature(models.Model):
    code = models.CharField(
        max_length=50, choices=UserRoleFeature.choices, unique=True
    )

    def __str__(self):
        return self.get_code_display()

    @staticmethod
    def get_worker_features() -> list:
        return [
            Feature.objects.filter(code='change_basic_task_status').get(),
        ]


class UserRole(models.Model):
    name = models.CharField(unique=True, max_length=50)
    features = models.ManyToManyField(Feature, blank=True)

    def has_feature(self, feature_code: str) -> bool:
        return self.features.filter(code=feature_code).exists()

    def __str__(self):
        return self.name


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


class TagColor(models.TextChoices):
    RED = "ff0000", "Red"
    BLUE = "0000ff", "Blue"
    GREEN = "00ff00", "Green"
    YELLOW = "ffff00", "Yellow"
    ORANGE = "ffa500", "Orange"
    PURPLE = "800080", "Purple"
    PINK = "ffc0cb", "Pink"
    BLACK = "000000", "Black"
    WHITE = "ffffff", "White"
    GRAY = "808080", "Gray"
    CYAN = "00ffff", "Cyan"
    MAGENTA = "ff00ff", "Magenta"
    BROWN = "a52a2a", "Brown"


class Tag(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=6, choices=TagColor.choices, default=TagColor.GRAY)

    class Meta:
        verbose_name_plural = "Tags"
        verbose_name = "Tag"

    def __str__(self):
        return self.name
