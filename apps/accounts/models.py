from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager

from rentit import settings
from utils.random_filename import RandomFileName


class MyUserManager(UserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    picture = models.ImageField(
        verbose_name="user avatar",
        blank=True,
        default=settings.MEDIA_URL + "user.png",
        upload_to=RandomFileName("avatars"),
    )
    phone = models.CharField(
        verbose_name="phone number",
        max_length=20,
        unique=True,
    )
    is_premium = models.BooleanField(
        default=False,
        help_text="Доступен ли пользователю премиум-функционал",
    )
    # TODO: Move premium and payments info into a new model
    premium_start_date = models.DateTimeField(null=True)
    premium_finish_date = models.DateTimeField(null=True)
    last_payment_id = models.CharField(max_length=100, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("first_name", "last_name")

    objects = MyUserManager()
    backend = "django.contrib.auth.backends.ModelBackend"

    def __str__(self):
        return self.get_full_name()
