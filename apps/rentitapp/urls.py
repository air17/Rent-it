from django.urls import path

from . import views

app_name = "rentitapp"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("create", views.advertisement_create, name="create"),
    path("detail/<int:pk>", views.advertisement_view, name="advertisement"),
    path("edit/<int:pk>", views.advertisement_edit, name="edit"),
]
