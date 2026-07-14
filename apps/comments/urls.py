from django.urls import path

from . import views

app_name = "comments"

urlpatterns = [
    path("article/<slug:slug>/commenter/", views.poster, name="poster"),
]
