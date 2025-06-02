from django.contrib import admin
from .models.rent_home import RentHome
from .models.attributes import Attribute

@admin.register(RentHome)
class RentHomeAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'rooms', 'beds', 'area', 'price')
    list_filter = ('owner', 'rooms', 'price')
    search_fields = ('title', 'description', 'owner__username')
    filter_horizontal = ('attributes',)

@admin.register(Attribute)
class AttributesAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
