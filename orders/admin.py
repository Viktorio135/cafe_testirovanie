from django.contrib import admin

from .models import Item, Order, Table, OrderItem

admin.site.register(Item)
admin.site.register(Table)
admin.site.register(Order)
admin.site.register(OrderItem)