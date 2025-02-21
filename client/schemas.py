from ninja import ModelSchema

from client.models import Client, ClientMachine, ClientPlace


class ClientSchema(ModelSchema):
    client_places: list[dict]

    @staticmethod
    def resolve_client_places(obj: Client) -> list[dict]:
        client_places = obj.client_places.all()
        return [ClientPlaceSchema.from_orm(client_place).dict() for client_place in
                client_places] if client_places else []

    class Meta:
        model = Client
        fields = '__all__'


class ClientPlaceSchema(ModelSchema):
    client_machines: list[dict]

    @staticmethod
    def resolve_client_machines(obj: ClientPlace) -> list[dict]:
        client_machines = obj.client_machines.all()
        return [ClientMachineSchema.from_orm(client_machine).dict() for client_machine in
                client_machines] if client_machines else []

    class Meta:
        model = ClientPlace
        fields = '__all__'


class ClientMachineSchema(ModelSchema):
    class Meta:
        model = ClientMachine
        fields = '__all__'
