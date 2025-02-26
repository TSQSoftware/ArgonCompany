from django.contrib import admin

from form.models import Form, FormAnswer, Answer, QuestionCategory

admin.site.register(Form)


@admin.register(QuestionCategory)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'show_in_table')
    list_editable = ('order', 'show_in_table')
    search_fields = ('name',)
    ordering = ('order',)


from django.contrib import admin
from .models import Question


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'form', 'question_type', 'is_header', 'required', 'score', 'show_in_table')
    list_filter = ('category', 'form', 'question_type', 'is_header', 'required', 'show_in_table')
    search_fields = ('title', 'subtitle', 'category__name', 'form__name')

    fieldsets = (
        (None, {'fields': ('form', 'category')}),
        ('Question Details', {
            'fields': ('title', 'subtitle', 'question_type', 'choices', 'is_header', 'show_in_table'),
        }),
        ('Dependencies & Relations', {
            'fields': ('depends_on', 'parent_question'),
        }),
        ('Validation & Scoring', {
            'fields': ('required', 'validation_rules', 'score'),
        }),
        ('Additional Information', {
            'fields': ('columns', 'media_url'),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field_name in ['choices', 'columns', 'validation_rules']:
            if field_name in form.base_fields:
                form.base_fields[field_name].widget.attrs['style'] = 'width: 70%;'
        return form


admin.site.register(FormAnswer)
admin.site.register(Answer)
