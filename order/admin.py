from django.contrib import admin

from order.models import Order, OrderType

admin.site.register(OrderType)
admin.site.register(Order)