# tracker/admin.py
from django.contrib import admin
from .models import LocationUpdate

@admin.register(LocationUpdate)
class LocationUpdateAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'latitude', 'longitude')
    readonly_fields = ('timestamp',)
    list_filter = ('timestamp',)
    date_hierarchy = 'timestamp'
