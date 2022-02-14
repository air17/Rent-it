import pytest

from . import models


@pytest.mark.django_db
def test_user_model():
    models.User.objects.create(
        first_name="Test",
        last_name="Test",
        email="test@test.ru",
        phone="+79777777777",
    )
    user = models.User.objects.get(email="test@test.ru")
    assert user.first_name == "Test"
    assert user.is_premium is False
