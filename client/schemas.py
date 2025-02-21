from ninja import ModelSchema

from client.models import Client, ClientMachine, ClientPlace


class ClientSchema(ModelSchema):
    class Meta:
        model = Client
        fields = '__all__'

class ClientPlaceSchema(ModelSchema):
    class Meta:
        model = ClientPlace
        fields = '__all__'

class ClientMachineSchema(ModelSchema):
    class Meta:
        model = ClientMachine
        fields = '__all__'