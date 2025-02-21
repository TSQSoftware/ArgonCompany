from ninja import ModelSchema

from data.models import TaskCategory, Tag


class TaskCategorySchema(ModelSchema):
    class Meta:
        model = TaskCategory
        fields = '__all__'

class TagSchema(ModelSchema):
    class Meta:
        model = Tag
        fields = '__all__'