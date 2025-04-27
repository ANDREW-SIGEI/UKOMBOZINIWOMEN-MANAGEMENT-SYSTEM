from django.contrib import admin
from .models import Booster

@admin.register(Booster)
class BoosterAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',) 