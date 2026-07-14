from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.feedgenerator import Rss201rev2Feed

from apps.articles.models import Article, Categorie

from .models import ParametresSite


class DernieresActualites(Feed):
    feed_type = Rss201rev2Feed

    def title(self):
        return ParametresSite.load().nom_site

    def description(self):
        return ParametresSite.load().slogan

    def link(self):
        return reverse("articles:home")

    def items(self):
        return Article.objects.publies().select_related("categorie")[:30]

    def item_title(self, item):
        return item.titre

    def item_description(self, item):
        return item.chapeau

    def item_link(self, item):
        return item.get_absolute_url()

    def item_pubdate(self, item):
        return item.date_publication

    def item_categories(self, item):
        return [item.categorie.nom]


class RubriqueFeed(DernieresActualites):
    def get_object(self, request, slug):
        return Categorie.objects.get(slug=slug)

    def title(self, obj):
        return f"{obj.nom} — {ParametresSite.load().nom_site}"

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return obj.description or f"Actualités : {obj.nom}"

    def items(self, obj):
        return obj.articles_publies.select_related("categorie")[:30]
