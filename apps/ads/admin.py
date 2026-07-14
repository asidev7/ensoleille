from django.contrib import admin

from .models import AdSenseConfig, Publicite


@admin.register(Publicite)
class PubliciteAdmin(admin.ModelAdmin):
    list_display = ("titre", "emplacement", "actif", "impressions", "clics", "ctr")
    list_filter = ("emplacement", "actif")


@admin.register(AdSenseConfig)
class AdSenseConfigAdmin(admin.ModelAdmin):
    list_display = ("client_id", "actif", "auto_ads")
