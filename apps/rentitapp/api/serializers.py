from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import HyperlinkedRelatedField, ModelSerializer

from apps.rentitapp.models import Advertisement, Comment


class CommentSerializer(ModelSerializer):
    author = SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = (
            "author",
            "text",
            "date_published",
        )

    @staticmethod
    def get_author(obj):
        if obj.author:
            return obj.author.get_full_name()


class AdvertisementSerializer(ModelSerializer):
    author = HyperlinkedRelatedField(view_name="user-detail", read_only=True)

    class Meta:
        model = Advertisement
        exclude = ("active",)


class ThinAdvertisementSerializer(ModelSerializer):
    class Meta:
        model = Advertisement
        fields = (
            "picture",
            "category",
            "name",
            "price",
            "address",
            "url",
        )
