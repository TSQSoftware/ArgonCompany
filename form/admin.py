from django.contrib import admin

from form.models import Form, FormAnswer, Question, Answer, QuestionCategory

admin.site.register(Form)


@admin.register(QuestionCategory)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'show_in_table')
    list_editable = ('order', 'show_in_table')
    search_fields = ('name',)
    ordering = ('order',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'form')
    list_filter = ('category', 'form')
    fieldsets = (
        (None, {'fields': ('form', 'category')}),
        ('Question Details', {
            'fields': ('title', 'subtitle', 'question_type', 'choices')
        }),
    )


admin.site.register(FormAnswer)
admin.site.register(Answer)
