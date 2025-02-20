from django.contrib import admin

from worker.models import Worker, WorkerLocation

admin.site.register(Worker)
admin.site.register(WorkerLocation)