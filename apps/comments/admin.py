from django.contrib import admin

from .models import Commentaire


@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display = ("nom", "article", "approuve", "created_at")
    list_filter = ("approuve",)
    actions = ["approuver"]

    @admin.action(description="Approuver les commentaires sélectionnés")
    def approuver(self, request, queryset):
        queryset.update(approuve=True)
