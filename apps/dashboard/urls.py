from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("connexion/", auth_views.LoginView.as_view(template_name="dashboard/login.html"), name="login"),
    path("deconnexion/", auth_views.LogoutView.as_view(), name="logout"),

    path("", views.home, name="home"),

    # Articles
    path("articles/", views.articles_liste, name="articles"),
    path("articles/nouveau/", views.article_form, name="article_creer"),
    path("articles/<int:pk>/modifier/", views.article_form, name="article_modifier"),
    path("articles/<int:pk>/supprimer/", views.article_supprimer, name="article_supprimer"),

    # Commentaires
    path("commentaires/", views.commentaires, name="commentaires"),
    path("commentaires/<int:pk>/<str:action>/", views.commentaire_action, name="commentaire_action"),

    # Publicités
    path("publicites/", views.publicites, name="publicites"),
    path("publicites/nouvelle/", views.publicite_form, name="publicite_creer"),
    path("publicites/<int:pk>/modifier/", views.publicite_form, name="publicite_modifier"),
    path("publicites/<int:pk>/supprimer/", views.publicite_supprimer, name="publicite_supprimer"),
    path("adsense/", views.adsense_config, name="adsense"),

    # Rubriques & tags
    path("rubriques/", views.rubriques, name="rubriques"),
    path("rubriques/nouvelle/", views.rubrique_form, name="rubrique_creer"),
    path("rubriques/<int:pk>/modifier/", views.rubrique_form, name="rubrique_modifier"),
    path("tags/creer/", views.tag_creer, name="tag_creer"),

    # Auteurs
    path("auteurs/", views.auteurs, name="auteurs"),
    path("auteurs/nouveau/", views.auteur_form, name="auteur_creer"),
    path("auteurs/<int:pk>/modifier/", views.auteur_form, name="auteur_modifier"),

    # Newsletter
    path("newsletter/", views.newsletter, name="newsletter"),
    path("newsletter/export/", views.newsletter_export, name="newsletter_export"),

    # Paramètres
    path("parametres/", views.parametres, name="parametres"),
]
