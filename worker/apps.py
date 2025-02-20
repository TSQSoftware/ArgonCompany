import os
import sys

from django.apps import AppConfig
from django.core.management import call_command


class WorkerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'worker'


    def ready(self):
        """Runs when the app is loaded, executes update_license command."""
        if "runserver" in sys.argv and not os.environ.get("RUN_MAIN"):
            self.run_update_license()

    def run_update_license(self):
        """Executes update_license command and stops server if it fails."""
        try:
            call_command("send_update")  # Run the command
        except Exception as e:
            print(f"\n❌ Error running update_license: {e}\n")
            sys.exit(1)