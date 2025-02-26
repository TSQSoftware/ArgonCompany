from django.core.management.base import BaseCommand

from data.models import Feature, UserRoleFeature, UserRole
from tasks.models import TaskStatus


def first_time_setup(self: BaseCommand) -> None:
    if TaskStatus.objects.count() == 0:
        TaskStatus.objects.update_or_create(name="W realizacji")
        TaskStatus.objects.update_or_create(name="Zrealizowane", require_confirmation=True, completed=True)
        TaskStatus.objects.update_or_create(name="Anulowane", require_confirmation=True)
        TaskStatus.objects.update_or_create(name="Zlecone")
        TaskStatus.objects.update_or_create(name="Oczekuje potwierdzenia")

        self.stdout.write(self.style.SUCCESS("Task statuses created successfully."))

    for user_role in UserRoleFeature.choices:
        Feature.objects.update_or_create(code=user_role[0])

    self.stdout.write(self.style.SUCCESS("User features created or updated successfully."))

    if UserRole.objects.count() == 0:
        admin = UserRole.objects.create(
            name="Admin",
        )
        admin.features.set(Feature.objects.all())

        worker = UserRole.objects.create(
            name="Worker",
        )
        worker.features.set(Feature.get_worker_features())

        self.stdout.write(self.style.SUCCESS("User roles created or updated successfully."))
