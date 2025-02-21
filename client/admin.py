from django.contrib import admin

from client.models import ClientMachine, ClientObject, Client

admin.site.register(ClientMachine)
admin.site.register(ClientObject)
admin.site.register(Client)