from django.contrib import admin
from .models import Voucher, Order, OrderStatus, OrderItem
from account.models import Address
# Register your models here.

class OrderItemAdmin(admin.TabularInline):
    model = OrderItem

class OrderStatusAdmin(admin.TabularInline):
    model = OrderStatus

class OrdersAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'ref_id',
        'billing_address',
        'shipping_address',
        'customer_id',
        'order_type',
        'total_net',
        'created_at',
        'created_by'
    ]
    inlines = [
        OrderStatusAdmin, OrderItemAdmin
    ]


class OrderStatusAdmin2(admin.ModelAdmin):
    list_display = [
        'id',
        'order_id',
        'status',
        'created_at',
        'created_by',
    ]

admin.site.register(Order, OrdersAdmin)

admin.site.register(OrderStatus, OrderStatusAdmin2)

admin.site.register(Voucher)

