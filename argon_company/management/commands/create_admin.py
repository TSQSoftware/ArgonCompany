from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Creates a superuser with username 'data' and password 'data'."

    def handle(self, *args, **kwargs):
        user_model = get_user_model()

        if user_model.objects.filter(username="data").exists():
            return

        user = user_model.objects.create_superuser(username="data", password="data")
        user.is_active = True
        user.save()

        self.stdout.write(self.style.SUCCESS("Superuser 'data' created with password 'data'. Please change the password immediately."))
