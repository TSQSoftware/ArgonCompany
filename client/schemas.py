from ninja import ModelSchema

from client.models import Client, ClientMachine, ClientPlace
from data.schemas import TaskCategorySchema


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
    def resolve_machines(obj: ClientPlace) -> list[dict]:
        machines = obj.machines.all()
        return [ClientMachineSchema.from_orm(machine).dict() for machine in machines] if machines.exists() else []

    class Meta:
        model = ClientPlace
        fields = '__all__'


class ClientMachineSchema(ModelSchema):
    category: dict

    @staticmethod
    def resolve_category(obj: ClientMachine) -> dict:
        return TaskCategorySchema.from_orm(obj.category).dict()

    class Meta:
        model = ClientMachine
        fields = '__all__'
