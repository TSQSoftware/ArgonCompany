from django.contrib import admin

from tasks.models import Task, TaskNote

admin.site.register(Task)
admin.site.register(TaskNote)