from django.contrib import admin
from .models import Components, EmailComponent

# Register your models here.
class ComponentsAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'hierarchy_level',
        'parent_name',
        'date_deleted',
        'value',
    ]

class EmailComponentAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'first_name',
        'last_name',
        'email',
        'phone',
        'subject',
        'message',
        'date_created',
        'read'
    ]
    

admin.site.register(Components, ComponentsAdmin)
admin.site.register(EmailComponent, EmailComponentAdmin)
