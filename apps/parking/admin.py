from django.contrib import admin
from .models import Camera, ParkingSpace, Config

@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']

@admin.register(ParkingSpace)
class ParkingSpaceAdmin(admin.ModelAdmin):
    list_display = ['number', 'camera', 'is_occupied', 'updated_at']
    list_filter = ['camera', 'is_occupied']

@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'updated_at']
