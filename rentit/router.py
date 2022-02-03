from rest_framework.routers import DefaultRouter
from apps.accounts.api.views import UserViewSet
from apps.rentitapp.api.views import AdvertisementViewSet

router = DefaultRouter()
router.register("users", UserViewSet)
router.register("ads", AdvertisementViewSet)
