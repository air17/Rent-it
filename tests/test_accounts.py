import pytest
from django.contrib.auth.models import AnonymousUser
from pytest_django.asserts import assertContains
from django.http import Http404

from rentit.settings.components.common import STATIC_URL
from apps.accounts.views import profile_view, account_view, registration_view


@pytest.mark.django_db
def test_user_model(django_user_model):
    django_user_model.objects.create_user(
        first_name="Test",
        last_name="Test",
        email="test@test.ru",
        phone="+79777777777",
    )
    user = django_user_model.objects.get(email="test@test.ru")
    user.membership.plan = user.membership.Plans.PREMIUM
    user.membership.save()
    assert user.membership.plan == user.membership.Plans.FREE
    assert user.first_name == "Test"
    assert user.is_premium is False
    assert user.get_full_name() == "Test Test"
    assert user.avatar_url == STATIC_URL + "user.png"


@pytest.mark.django_db
def test_create_superuser(django_user_model):
    with pytest.raises(ValueError):
        django_user_model.objects.create_superuser(email=None)
    django_user_model.objects.create_superuser("admin@test.ru", "0000")
    admin = django_user_model.objects.get(email="admin@test.ru")
    assert admin.is_superuser is True


def test_profile_view(rf, admin_user):
    request = rf.get("")
    request.user = admin_user
    response = profile_view(request, 1)
    assert response.status_code == 200
    with pytest.raises(Http404):
        profile_view(request, 25)
    assertContains(response, "Адрес: <i>Condimentum, Nam vehicula, 15</i>")


def test_account_view(rf, django_user_model):
    request = rf.get("")
    request.user = django_user_model.objects.get(id=2)
    response = account_view(request)
    assert response.status_code == 200
    assertContains(response, "User Userenko")


def test_registration_view(rf, client, admin_user):
    request = rf.get("")

    request.user = admin_user
    response = registration_view(request)
    assert response.status_code == 302

    request.user = AnonymousUser
    response = registration_view(request)
    assert response.status_code == 200

    response = client.post(
        "/profile/register",
        {
            "email": "email@email.ru",
            "first_name": "Test name",
            "last_name": "Test surname",
            "phone": "123456789",
            "password1": "BI68Srbo39r7nd3s374",
            "password2": "BI68Srbo39r7nd3s374",
        },
    )
    assert response.status_code == 302
