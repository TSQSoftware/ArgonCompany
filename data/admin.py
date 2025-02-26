from django.contrib import admin

from data.models import TaskCategory, Tag, UserRole, Color, Feature

admin.site.register(TaskCategory)
admin.site.register(Tag)
admin.site.register(UserRole)
admin.site.register(Color)
admin.site.register(Feature)