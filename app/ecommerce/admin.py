from django.contrib import admin

# Register your models here.
from .models import Item, ItemsImage, ItemsInventory, Category, Attribute


class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'hierarchy_level',
        'parent_id',
        'date_deleted',
        'slug_url'
    ]

class AttributeAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'hierarchy_level',
        'parent_id',
        'date_deleted',
        'is_filtered',
        'presentation'
    ]

class ItemsInventoryInline(admin.TabularInline):
    model = ItemsInventory
class ImageInline(admin.StackedInline):
    model = ItemsImage
class ItemAdmin(admin.ModelAdmin):
    list_display = [
        'item_id',
        'title',
        'price',
        'category',
        'slug',
        'created_date_time',
        'modified_date_time',
        'date_deleted',
        'images',
    ]
    inlines = [
        ItemsInventoryInline, ImageInline
    ]


admin.site.register(Item, ItemAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Attribute, AttributeAdmin)