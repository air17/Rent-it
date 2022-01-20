from django.urls import path
from api.views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register("ads", AdvertisementViewSet)

urlpatterns = router.urls
urlpatterns += [
    path('users/<int:pk>/', UserView.as_view(), name='user'),
    path('comments/<int:pk>/', get_comment, name='comment'),
]
