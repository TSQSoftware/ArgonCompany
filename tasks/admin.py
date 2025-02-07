from django.contrib import admin

from tasks.models import Task, TaskType

admin.site.register(TaskType)
admin.site.register(Task)