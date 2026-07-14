from django.urls import path

from . import views

app_name = "articles"

urlpatterns = [
    path("", views.home, name="home"),
    path("recherche/", views.recherche, name="recherche"),
    path("rubrique/<slug:slug>/", views.rubrique, name="rubrique"),
    path("auteur/<int:pk>/", views.auteur, name="auteur"),
    path("tag/<slug:slug>/", views.tag, name="tag"),
    path("article/<slug:slug>/", views.detail, name="detail"),
]
