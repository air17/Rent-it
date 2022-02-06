from django.urls import path
from .views import payment_view, process_notification, payment_processing_view

app_name = "payments"

urlpatterns = (
    path("yookassa_notification/", process_notification, name="yookassa_webhook"),
    path("premium/", payment_view, name="premium"),
    path("redirect/", payment_processing_view),
)
