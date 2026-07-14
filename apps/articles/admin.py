from django.contrib import admin

from .models import Article, Auteur, Categorie, Tag


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ("nom", "ordre", "en_menu", "couleur")
    list_editable = ("ordre", "en_menu")
    prepopulated_fields = {"slug": ("nom",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("nom",)}


@admin.register(Auteur)
class AuteurAdmin(admin.ModelAdmin):
    list_display = ("nom", "role")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("titre", "categorie", "statut", "a_la_une", "urgent", "date_publication", "nombre_vues")
    list_filter = ("statut", "categorie", "a_la_une", "urgent")
    search_fields = ("titre", "chapeau", "contenu")
    prepopulated_fields = {"slug": ("titre",)}
    date_hierarchy = "date_publication"
    autocomplete_fields = ()
