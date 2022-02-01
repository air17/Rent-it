from datetime import timedelta, datetime
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from .serializers import UserSerializer, CommentSerializer, ThinAdvertisementSerializer, ReadAdvertisementSerializer
from apps.rentitapp.models import Advertisement, Comment


class UserView(RetrieveAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


@api_view(['GET'])
def get_comment(request, pk, *args, **kwargs):
    comment = Comment.objects.get(pk=pk)
    serializer = CommentSerializer(comment, context={"request": request})
    return Response(serializer.data)


class AdvertisementViewSet(ReadOnlyModelViewSet):
    queryset = Advertisement.objects.all()
    # queryset = Advertisement.objects.filter(date_published__lte=datetime.now()-timedelta(days=2))
    serializer_class = ReadAdvertisementSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
