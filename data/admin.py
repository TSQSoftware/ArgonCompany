from django.contrib import admin

from data.models import TaskCategory, Tag

admin.site.register(TaskCategory)
admin.site.register(Tag)