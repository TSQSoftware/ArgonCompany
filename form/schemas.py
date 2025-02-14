from ninja import ModelSchema

from form.models import Form, FormAnswer


class FormSchema(ModelSchema):
    class Meta:
        model = Form
        fields = '__all__'

class SimpleFormSchema(ModelSchema):
    class Meta:
        model = Form
        fields = ('id', 'name')

class FormAnswerSchema(ModelSchema):
    class Meta:
        model = FormAnswer
        fields = '__all__'