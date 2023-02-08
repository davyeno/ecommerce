from django.contrib import admin
from .models import Customer, Address
# Register your models here.

class AddressAdmin(admin.StackedInline):
    model = Address

class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'customer_uuid',
        'first_name',
        'last_name',
        'phone_number',
        'email',
        'is_subcribe_email',
        'is_signup_user',
        'user',
        'date_joined',
        'date_deleted'
    ]
    inlines = [
        AddressAdmin
    ]

admin.site.register(Customer, CustomerAdmin)


