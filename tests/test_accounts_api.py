import pytest
import pytest_drf
from pytest_lambda import static_fixture

# Get access to db
pytestmark = pytest.mark.django_db
# Get a test user from db
user = pytest.fixture((lambda db, django_user_model: django_user_model.objects.get(id=2)))
# Create test admin user
admin = pytest.fixture((lambda admin_user: admin_user))

users_url = "/api/v1/users/"


class TestUserCreate(
    pytest_drf.APIViewTest,
    pytest_drf.Returns201,
    pytest_drf.UsesPostMethod,
    pytest_drf.UsesListEndpoint,
):
    @pytest.fixture
    def url(self):
        return users_url

    new_user = {
        "first_name": "Test_name",
        "last_name": "Test_surname",
        "email": "test@email.com",
        "phone": "999",
        "password": "1234",
    }

    data = static_fixture(new_user)


class TestUserDetail(
    pytest_drf.APIViewTest,
    pytest_drf.Returns200,
    pytest_drf.UsesGetMethod,
    pytest_drf.UsesDetailEndpoint,
    pytest_drf.ForbidsAnonymousUsers,
    pytest_drf.AsUser("user"),
):
    @pytest.fixture
    def url(self):
        return users_url + "1/"

    def test_it_returns_correct_first_name(self, json):
        expected = "Admin"
        actual = json.get("first_name")
        assert actual == expected


class TestUserList(
    pytest_drf.APIViewTest,
    pytest_drf.UsesGetMethod,
    pytest_drf.UsesListEndpoint,
    pytest_drf.AsUser("user"),
    pytest_drf.Returns403,
    pytest_drf.AsUser("admin"),
    pytest_drf.Returns200,
):
    @pytest.fixture
    def url(self):
        return users_url


class TestUserUpdate(
    pytest_drf.APIViewTest,
    pytest_drf.UsesPatchMethod,
    pytest_drf.ForbidsAnonymousUsers,
    pytest_drf.AsUser("user"),
    pytest_drf.Returns200,
    pytest_drf.AsUser("admin"),
    pytest_drf.Returns403,
):
    @pytest.fixture
    def url(self):
        return users_url + "2/"

    data = static_fixture({"first_name": "John", "phone": "123"})


class TestUserDestroy(
    pytest_drf.APIViewTest,
    pytest_drf.UsesDeleteMethod,
    pytest_drf.ForbidsAnonymousUsers,
    pytest_drf.AsUser("user"),
    pytest_drf.Returns403,
    pytest_drf.AsUser("admin"),
    pytest_drf.Returns204,
):
    @pytest.fixture
    def url(self):
        return users_url + "2/"
