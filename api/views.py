from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from api.serializers import UserSerializer, AdvertisementSerializer, ThinAdvertisementSerializer
from rentitapp.models import Advertisement


class UserViewSet(ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser, )


class AdvertisementViewSet(ModelViewSet):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer

    def list(self, request, *args, **kwargs):
        # notes = Advertisement.objects.filter(author=request.user.id)
        notes = self.queryset
        serializer = ThinAdvertisementSerializer(notes, many=True, context={"request": request})
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
