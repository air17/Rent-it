from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('<int:pk>', views.UserView.as_view(), name='userprofile'),
    path('', views.account_view, name='account'),
    path('register', views.registration, name='registration'),
    path('premium', views.premium_view, name='premium'),
    path('premium/payment', views.payment_view, name='payment'),
]
