from ninja import ModelSchema

from data.models import TaskCategory


class TaskCategorySchema(ModelSchema):
    class Meta:
        model = TaskCategory
        fields = '__all__'