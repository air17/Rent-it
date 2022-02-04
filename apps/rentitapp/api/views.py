from datetime import timedelta, datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .permissions import IsAuthor
from .serializers import AdvertisementSerializer, ThinAdvertisementSerializer
from apps.rentitapp.models import Advertisement


class AdvertisementViewSet(ModelViewSet):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def list(self, request, *args, **kwargs):
        if request.user and not (request.user.is_superuser or request.user.is_premium):
            day_ago = datetime.now() - timedelta(days=1)
            self.queryset = Advertisement.objects.filter(date_published__lte=day_ago)

        self.serializer_class = ThinAdvertisementSerializer

        return super().list(request, *args, **kwargs)

    def get_permissions(self):
        if self.action == "update":
            self.permission_classes += (IsAuthor,)

        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
