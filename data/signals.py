from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from argon_company.management.commands.setup import first_time_setup


@receiver(post_migrate)
def setup(sender, **kwargs):
    if sender.name != "data":
        return

    user_model = get_user_model()

    if not user_model.objects.filter(username="admin").exists():
        user = user_model.objects.create_superuser(username="admin", password="admin")
        user.is_active = True
        user.save()

    first_time_setup(None)
