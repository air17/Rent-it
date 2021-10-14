from django.urls import path

from . import views

app_name = 'rentitapp'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('profile/<int:pk>', views.UserView.as_view(), name='userprofile'),
    path('profile', views.account_view, name='account'),
    path('create', views.advertisement_create, name='create'),
    path('detail/<int:pk>', views.advertisement_view, name='advertisement'),
    path('edit/<int:pk>', views.advertisement_edit, name='edit'),
    path('profile/register', views.registration, name='registration'),
    path('profile/premium', views.premium_view, name='premium'),
    path('profile/premium/payment', views.payment_view, name='payment'),
]
