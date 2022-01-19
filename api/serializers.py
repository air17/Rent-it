from django.contrib.auth import get_user_model
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework.serializers import ModelSerializer

from rentitapp.models import Advertisement


class UserSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "password", "first_name", "last_name", "is_superuser")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data: dict):
        user = self.Meta.model(**validated_data)
        user.save()
        return user

    def update(self, instance, validated_data: dict):
        instance.set_password(validated_data.pop("password", ""))
        return super().update(instance, validated_data)


class AdvertisementSerializer(ModelSerializer):
    author = SerializerMethodField(read_only=True)

    def get_author(self, obj):
        if obj.author:
            return obj.author.email

    class Meta:
        model = Advertisement
        fields = ("id", "name", "description", "author", "price", "address", "category", "url")


class ThinAdvertisementSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name="advertisement-detail")

    class Meta:
        model = Advertisement
        fields = ("name", "price", "address", "category", "url")
