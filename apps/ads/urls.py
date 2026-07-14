from django.urls import path

from . import views

app_name = "ads"

urlpatterns = [
    path("pub/<int:pk>/clic/", views.clic, name="clic"),
]
