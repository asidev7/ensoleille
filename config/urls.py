from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from apps.core.feeds import DernieresActualites, RubriqueFeed
from apps.core.sitemaps import ArticleSitemap, CategorieSitemap, StatiquesSitemap
from apps.core.views import ads_txt, robots_txt

sitemaps = {
    "articles": ArticleSitemap,
    "categories": CategorieSitemap,
    "statiques": StatiquesSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", include("apps.dashboard.urls")),
    path("", include("apps.core.urls")),
    path("", include("apps.ads.urls")),
    path("", include("apps.comments.urls")),
    # SEO & flux
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", robots_txt, name="robots"),
    path("ads.txt", ads_txt, name="ads_txt"),
    path("rss/", DernieresActualites(), name="rss"),
    path("rss/rubrique/<slug:slug>/", RubriqueFeed(), name="rss_rubrique"),
    # Public (catch-all en dernier)
    path("", include("apps.articles.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "apps.core.errors.erreur_404"
handler500 = "apps.core.errors.erreur_500"
