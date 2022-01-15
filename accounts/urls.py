from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile/<int:pk>', views.UserView.as_view(), name='userprofile'),
    path('profile', views.account_view, name='account'),
    path('profile/register', views.registration, name='registration'),
    path('profile/premium', views.premium_view, name='premium'),
    path('profile/premium/payment', views.payment_view, name='payment'),
]
