from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creates a superuser with username 'admin' and password 'admin'."

    def handle(self, *args, **kwargs):
        user_model = get_user_model()

        if user_model.objects.filter(username="admin").exists():
            return

        user = user_model.objects.create_superuser(username="admin", password="admin")
        user.is_active = True
        user.save()

        self.stdout.write(self.style.SUCCESS(
            "Superuser 'admin' created with password 'admin'. Please change the password immediately."))
