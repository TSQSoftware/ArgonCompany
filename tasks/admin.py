from django.contrib import admin

from tasks.models import Task, TaskNote, TaskAttachment

admin.site.register(Task)
admin.site.register(TaskNote)
admin.site.register(TaskAttachment)