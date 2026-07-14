from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("a-propos/", views.a_propos, name="a_propos"),
    path("contact/", views.contact, name="contact"),
    path("mentions-legales/", views.mentions_legales, name="mentions_legales"),
    path("newsletter/", views.newsletter, name="newsletter"),
    path("newsletter/desinscription/<str:email>/", views.newsletter_desinscription, name="newsletter_desinscription"),
]
