from django.urls import path

from .views import premium_view

app_name = "subscriptions"

urlpatterns = [
    path("premium/", premium_view, name="premium"),
]
