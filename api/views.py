from datetime import timedelta, datetime
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from api.serializers import UserSerializer, CommentSerializer, ThinAdvertisementSerializer, ReadAdvertisementSerializer
from rentitapp.models import Advertisement, Comment


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

    def list(self, request, *args, **kwargs):
        advertisements = self.queryset
        for ad in advertisements:
            photo_path = ad.images.objects.first().image.url
            ad.main_photo = request.build_absolute_uri(photo_path)
        serializer = ThinAdvertisementSerializer(advertisements, many=True, context={"request": request})
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        ad = self.get_object()

        images_urls = []
        for img_obj in ad.images.objects.all():
            photo_path = img_obj.image.url
            images_urls.append(request.build_absolute_uri(photo_path))
        ad.images = images_urls

        ad.comments = []
        for comment in Comment.objects.filter(advertisement=ad):
            ad.comments.append(CommentSerializer(comment).data)

        serializer = ReadAdvertisementSerializer(ad, context={"request": request})
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

