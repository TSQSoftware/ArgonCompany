from django.contrib import admin

from client.models import ClientMachine, ClientPlace, Client

admin.site.register(ClientMachine)
admin.site.register(ClientPlace)
admin.site.register(Client)