from django.contrib import admin

from .models import AbonneNewsletter, MessageContact, ParametresSite


@admin.register(ParametresSite)
class ParametresSiteAdmin(admin.ModelAdmin):
    list_display = ("nom_site", "slogan")


@admin.register(AbonneNewsletter)
class AbonneNewsletterAdmin(admin.ModelAdmin):
    list_display = ("email", "actif", "created_at")


@admin.register(MessageContact)
class MessageContactAdmin(admin.ModelAdmin):
    list_display = ("nom", "sujet", "traite", "created_at")
    list_filter = ("traite",)
