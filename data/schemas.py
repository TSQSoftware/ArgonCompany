from ninja import ModelSchema

from data.models import TaskCategory, Tag, UserRole


class TaskCategorySchema(ModelSchema):
    class Meta:
        model = TaskCategory
        fields = '__all__'

class TagSchema(ModelSchema):
    class Meta:
        model = Tag
        fields = '__all__'

class UserRoleSchema(ModelSchema):
    features: list[str]

    @staticmethod
    def resolve_features(obj: 'UserRole') -> list:
        return [feature.code for feature in obj.features.all()]

    class Meta:
        model = UserRole
        fields = '__all__'