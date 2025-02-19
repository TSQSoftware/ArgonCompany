from cx_Freeze import setup, Executable
import os

# Ustawienie zmiennych środowiskowych Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'argon_company.settings'

# Główna aplikacja Django Ninja
executables = [
    Executable("manage.py", base=None, target_name="ArgonCompany")
]

# Opcje cx_Freeze
options = {
    "build_exe": {
        "packages": ["os", "django", "ninja"],
        "include_files": ["argon_company/"],  # Zmień na folder projektu Django
        "excludes": ["tkinter"],  # Opcjonalnie
    }
}

setup(
    name="ArgonCompany",
    version="1.0",
    description="aplikacja ArgonCompany",
    options=options,
    executables=executables,
)
