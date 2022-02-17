import pytest
from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from django.utils import timezone
from pytest_django.asserts import assertContains

from apps.rentitapp.models import Advertisement
from apps.rentitapp.views import (
    advertisement_list,
    advertisement_detail,
    advertisement_edit,
    advertisement_create,
    advertisement_process,
    comment_processing,
)
from utils.get_temporary_image import get_temporary_image

test_ad_uuid = "76a8112d-4270-430a-a725-40b99799d31e"


def test_advertisement_list_view(rf, db):
    request = rf.get("", data={"category": Advertisement.FlatCategory.ROOM})
    request.user = AnonymousUser
    response = advertisement_list(request)
    assert response.status_code == 200
    assertContains(response, "Ipsum lorum")


def test_advertisement_detail_view(rf, admin_user, django_user_model):
    ad = Advertisement.objects.get(id=test_ad_uuid)
    ad.date_published = timezone.now()
    ad.save()

    request = rf.get("", data={"edited": 1})

    request.user = admin_user
    response = advertisement_detail(request, test_ad_uuid)
    assert response.status_code == 302

    request.user = django_user_model.objects.get(id=1)
    response = advertisement_detail(request, test_ad_uuid)
    assert response.status_code == 200
    with pytest.raises(Http404):
        advertisement_detail(request, "00000000-0000-0000-0000-000000000000")
    assertContains(response, "Адрес: Mauris iaculis, 152")
    assertContains(response, "отредактировано")


def test_advertisement_edit_view(rf, django_user_model, admin_user):
    request = rf.get("")

    request.user = admin_user
    response = advertisement_edit(request, test_ad_uuid)
    assert response.status_code == 302
    with pytest.raises(Http404):
        advertisement_edit(request, "00000000-0000-0000-0000-000000000000")

    request.user = django_user_model.objects.get(id=2)
    response = advertisement_edit(request, test_ad_uuid)
    assert response.status_code == 200

    request = rf.post(
        "",
        {
            "name": "New Title",
            "category": Advertisement.FlatCategory.FLAT,
            "description": "Nothing",
            "price": 25,
            "address": "-",
            "picture": "same.jpg",
        },
    )
    request.user = django_user_model.objects.get(id=2)
    response = advertisement_edit(request, test_ad_uuid)
    assert response.status_code == 302
    assert response.url.endswith("edited=1") is True


def test_advertisement_create_view(rf, admin_user):
    request = rf.get("")
    request.user = admin_user
    response = advertisement_create(request)
    assert response.status_code == 200

    request = rf.post(
        "",
        {
            "name": "New Title",
            "category": Advertisement.FlatCategory.HOUSE,
            "description": "House description",
            "price": 25000,
            "address": "New Avenue, 25",
            "picture": get_temporary_image(),
        },
    )
    request.user = admin_user
    response = advertisement_create(request)
    assert response.status_code == 302
    assert response.url.endswith("success=1") is True


def test_advertisement_process_view(rf, django_user_model, admin_user):
    request_deactivate = rf.get("", data={"deactivate": 1})
    request_deactivate.user = admin_user
    response = advertisement_process(request_deactivate, test_ad_uuid)
    assert response.url == "/"

    test_ad = Advertisement.objects.get(id=test_ad_uuid)
    assert test_ad.active is True

    request_deactivate.user = django_user_model.objects.get(id=2)
    advertisement_process(request_deactivate, test_ad_uuid)
    test_ad.refresh_from_db()
    assert test_ad.active is False

    request_activate = rf.get("", data={"activate": 1})
    request_activate.user = django_user_model.objects.get(id=2)
    advertisement_process(request_activate, test_ad_uuid)
    test_ad.refresh_from_db()
    assert test_ad.active is True

    request_delete = rf.get("", data={"delete": 1})
    request_delete.user = django_user_model.objects.get(id=2)
    advertisement_process(request_deactivate, test_ad_uuid)
    advertisement_process(request_delete, test_ad_uuid)
    with pytest.raises(test_ad.DoesNotExist):
        test_ad.refresh_from_db()


def test_comment_process_view(rf, django_user_model, admin_user):
    request = rf.get("", data={"comment": "blah-blah"})
    request.user = admin_user
    response = comment_processing(request, test_ad_uuid)
    assert response.url.endswith("comment_added=1") is True

    response = comment_processing(request, test_ad_uuid)
    assert response.url.endswith("comment_added=error") is True
