from django.contrib.auth import get_user_model
from rest_framework.fields import SerializerMethodField, URLField, JSONField
from rest_framework.serializers import ModelSerializer, HyperlinkedRelatedField

from apps.rentitapp.models import Advertisement, Comment


class UserSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("picture", "first_name", "last_name", "email", "phone", )


class CommentSerializer(ModelSerializer):
    author = SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = ("author", "text", "date_published", )

    def get_author(self, obj):
        if obj.author:
            return obj.author.get_full_name()


class ReadAdvertisementSerializer(ModelSerializer):
    author = HyperlinkedRelatedField(view_name='user', read_only=True)
    comments = JSONField(read_only=True)

    class Meta:
        model = Advertisement
        exclude = ("active",)


class ThinAdvertisementSerializer(ModelSerializer):
    class Meta:
        model = Advertisement
        fields = ("name", "price", "address", "category", "url", "picture")
