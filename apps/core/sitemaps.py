from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.articles.models import Article, Categorie


class ArticleSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Article.objects.publies()

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class CategorieSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.6

    def items(self):
        return Categorie.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()


class StatiquesSitemap(Sitemap):
    priority = 0.4

    def items(self):
        return ["articles:home", "core:a_propos", "core:contact", "core:mentions_legales"]

    def location(self, item):
        return reverse(item)
