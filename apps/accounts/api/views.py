from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .permissions import IsOwner, IsSuperUser
from .serializers import UserSerializer


class UserViewSet(ModelViewSet):

    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def get_permissions(self):
        if self.action in ("list", "destroy"):
            self.permission_classes += (IsSuperUser,)
        elif self.action == "update":
            self.permission_classes += (IsOwner,)
        return super(self.__class__, self).get_permissions()
