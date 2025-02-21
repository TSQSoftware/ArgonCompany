from ninja import ModelSchema

from client.models import Client


class ClientSchema(ModelSchema):
    class Meta:
        model = Client
        fields = '__all__'