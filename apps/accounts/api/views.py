from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.viewsets import ModelViewSet

from .permissions import IsOwner
from .serializers import UserSerializer


class UserViewSet(ModelViewSet):

    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.action in ("list", "destroy"):
            self.permission_classes += (IsAdminUser,)
        elif self.action == "update":
            self.permission_classes += (IsOwner,)
        elif self.action == "create":
            self.permission_classes = (AllowAny,)
        return super().get_permissions()
