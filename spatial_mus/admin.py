from django.contrib.gis import admin

from .models import ManagementUnit


@admin.register(ManagementUnit)
class ManagementUnitModelAdmin(admin.GeoModelAdmin):
    list_display = ("label", "lake", "mu_type", "description")
    list_filter = ("lake", "mu_type")
    search_fields = ("label",)
