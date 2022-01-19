from api.views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register("users", UserViewSet)
router.register("ads", AdvertisementViewSet)

urlpatterns = router.urls
