from ninja import ModelSchema

from form.models import Form, FormAnswer, Question, Answer


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

class QuestionSchema(ModelSchema):
    class Meta:
        model = Question
        fields = '__all__'

class AnswerSchema(ModelSchema):
    class Meta:
        model = Answer
        fields = '__all__'