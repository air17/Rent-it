from django.urls import path
from . import views

app_name = "rentitapp"

urlpatterns = [
    path("", views.advertisement_list, name="index"),
    path("create", views.advertisement_create, name="create"),
    path("detail/<uuid:pk>", views.advertisement_detail, name="advertisement"),
    path("edit/<uuid:pk>", views.advertisement_edit, name="edit"),
    path("process_ad/<uuid:pk>", views.advertisement_process, name="process"),
    path("process_comment/<uuid:pk>", views.comment_processing, name="comment"),
]
