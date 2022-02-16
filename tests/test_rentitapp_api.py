from io import BytesIO

import pytest
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from pytest_drf import (
    ViewSetTest,
    UsesGetMethod,
    UsesListEndpoint,
    ForbidsAnonymousUsers,
    AsUser,
    Returns200,
    Returns403,
    UsesDetailEndpoint,
    UsesPatchMethod,
    UsesDeleteMethod,
    Returns201,
    Returns204,
    UsesPostMethod,
)
from pytest_lambda import static_fixture

from apps.rentitapp.models import Advertisement

# Get access to db
pytestmark = pytest.mark.django_db
# Get a test user from db
user = pytest.fixture((lambda db, django_user_model: django_user_model.objects.get(id=2)))
# Create test admin user
admin = pytest.fixture((lambda admin_user: admin_user))

ads_url = "/api/v1/ads/"


class TestAdvertisementViewSet(ViewSetTest):
    @pytest.fixture
    def list_url(self):
        return ads_url

    @pytest.fixture
    def detail_url(self):
        return ads_url + "76a8112d-4270-430a-a725-40b99799d31e/"

    class TestList(
        UsesGetMethod,
        UsesListEndpoint,
        ForbidsAnonymousUsers,
        AsUser("user"),
        Returns200,
    ):
        pass

    class TestRetrieve(
        UsesGetMethod,
        UsesDetailEndpoint,
        ForbidsAnonymousUsers,
        AsUser("user"),
        Returns200,
    ):
        pass

    class TestUpdate(
        UsesPatchMethod,
        UsesDetailEndpoint,
        ForbidsAnonymousUsers,
        AsUser("user"),
        Returns200,
        AsUser("admin"),
        Returns403,
    ):
        pass

    class TestDelete(
        UsesDeleteMethod,
        UsesDetailEndpoint,
        ForbidsAnonymousUsers,
        AsUser("user"),
        Returns204,
        AsUser("admin"),
        Returns403,
    ):
        pass

    class TestCreate(
        UsesPostMethod,
        UsesListEndpoint,
        AsUser("user"),
        Returns201,
    ):
        @staticmethod
        def get_temporary_image():
            file = BytesIO()
            img = Image.new("RGB", (100, 100))
            img.save(file, "jpeg")
            return SimpleUploadedFile("test.jpg", file.getvalue())

        new_ad = {
            "category": Advertisement.FlatCategory.FLAT,
            "name": "Flat name",
            "description": "Flat desc",
            "price": 999,
            "address": "Flat address",
            "picture": get_temporary_image(),
        }

        data = static_fixture(new_ad)
