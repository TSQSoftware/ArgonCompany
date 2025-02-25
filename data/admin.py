from django.contrib import admin

from data.models import TaskCategory, Tag, UserRole

admin.site.register(TaskCategory)
admin.site.register(Tag)
admin.site.register(UserRole)