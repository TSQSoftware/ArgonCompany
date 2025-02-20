import json
import requests
from django.core.management.base import BaseCommand
from pathlib import Path

from argon_company import settings


class Command(BaseCommand):
    help = "Reads license.json and sends a PATCH request to update the server"

    def handle(self, *args, **kwargs):
        license_path = Path(settings.BASE_DIR) / "license.json"

        if not license_path.exists():
            raise FileNotFoundError("license.json file not found in project root.")

        try:
            with open(license_path, "r") as file:
                license_data = json.load(file)
        except json.JSONDecodeError:
            raise ValueError("Failed to parse license.json.")

        license_id = license_data.get("id")
        license_uuid = license_data.get("uuid")

        if not license_id or not license_uuid:
            raise ValueError("Missing required fields (id, uuid) in license.json.")

        version = settings.VERSION
        url = f"{settings.CENTRAL_URL}api/v1/server/update?license_id={license_id}&license_uuid={license_uuid}"
        payload = {"version": version}

        try:
            response = requests.patch(url, json=payload, timeout=5)
            response.raise_for_status()
        except requests.RequestException as e:
            raise ConnectionError(f"Request failed: {e}. Do you have an active license?")

        self.stdout.write(self.style.SUCCESS(f"Success: {response.json()}"))
