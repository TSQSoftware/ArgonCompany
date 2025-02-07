from django.contrib import admin

from form.models import Form, FormAnswer, Question, Answer

admin.site.register(Form)
admin.site.register(Question)
admin.site.register(FormAnswer)
admin.site.register(Answer)

