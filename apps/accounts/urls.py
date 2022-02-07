from django.urls import path
from . import views
from ..subscriptions.views import premium_view

app_name = "accounts"

urlpatterns = [
    path("<int:pk>", views.profile_view, name="userprofile"),
    path("", views.account_view, name="account"),
    path("register", views.registration, name="registration"),
]
