from django.core.management.base import BaseCommand

from data.models import Feature, UserRoleFeature, UserRole, Color
from tasks.models import TaskStatus


def setup_data(print_messages=False, command=None):
    if TaskStatus.objects.count() == 0:
        TaskStatus.objects.update_or_create(name="W realizacji")
        TaskStatus.objects.update_or_create(name="Zrealizowane", require_confirmation=True, completed=True)
        TaskStatus.objects.update_or_create(name="Anulowane", require_confirmation=True)
        TaskStatus.objects.update_or_create(name="Zlecone")
        TaskStatus.objects.update_or_create(name="Oczekuje potwierdzenia")

        if print_messages and command:
            command.stdout.write(command.style.SUCCESS("Task statuses created successfully."))

    for user_role in UserRoleFeature.choices:
        Feature.objects.update_or_create(code=user_role[0])

    if print_messages and command:
        command.stdout.write(command.style.SUCCESS("User features created or updated successfully."))

    if UserRole.objects.count() == 0:
        admin = UserRole.objects.create(name="Admin")
        admin.features.set(Feature.objects.all())

        worker = UserRole.objects.create(name="Worker")
        worker.features.set(Feature.get_worker_features())

        if print_messages and command:
            command.stdout.write(command.style.SUCCESS("User roles created or updated successfully."))

    if Color.objects.count() != 0:
        return

    initial_colors = [
        ("Red", "ff0000"),
        ("Blue", "0000ff"),
        ("Green", "00ff00"),
        ("Yellow", "ffff00"),
        ("Orange", "ffa500"),
        ("Purple", "800080"),
        ("Pink", "ffc0cb"),
        ("Black", "000000"),
        ("White", "ffffff"),
        ("Gray", "808080"),
        ("Cyan", "00ffff"),
        ("Magenta", "ff00ff"),
        ("Brown", "a52a2a"),
    ]

    for name, color in initial_colors:
        Color.objects.get_or_create(name=name, color=color)


def first_time_setup(self: BaseCommand | None) -> None:
    setup_data(print_messages=True if self else False, command=self)
