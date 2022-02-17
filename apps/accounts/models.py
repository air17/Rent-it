import logging

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

from rentit.settings.components.common import STATIC_URL
from utils.random_filename import RandomFileName

logger = logging.getLogger(__name__)


class MyUserManager(UserManager):
    """Define a model manager for User model with no username field."""

    def _create_user(self, email, password, **extra_fields):  # skipcq
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):  # skipcq
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):  # skipcq
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Stores a user profile.

    All fields except picture are required.
    """

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
        null=True,
        upload_to=RandomFileName("avatars"),
    )
    phone = models.CharField(
        verbose_name="phone number",
        max_length=20,
        unique=True,
    )

    @property
    def avatar_url(self):
        """Path to a user picture"""
        if self.picture:
            return self.picture.url
        else:
            return STATIC_URL + "user.png"

    @property
    def is_premium(self):
        """Indicates if user has premium membership"""
        return self.membership.plan == Membership.Plans.PREMIUM

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("first_name", "last_name")

    objects = MyUserManager()
    backend = "django.contrib.auth.backends.ModelBackend"

    def save(self, *args, **kwargs):
        """Saves model to database and creates a Membership if it doesn't exist"""
        super(User, self).save(*args, **kwargs)
        Membership.objects.get_or_create(user=self)

    def __str__(self):
        return self.get_full_name()


class Membership(models.Model):
    """Stores User's membership plan, related to :model:`accounts.User`"""

    class Plans(models.IntegerChoices):
        FREE = 0, "Free"
        PREMIUM = 1, "Premium"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.IntegerField(
        choices=Plans.choices,
        default=Plans.FREE,
    )

    def save(self, *args, **kwargs):
        if self.plan == self.Plans.PREMIUM and not hasattr(self, "premiumsubscription"):
            self.plan = self.Plans.FREE
            logger.error("You cannot make premium membership without a subscription")
        return super(Membership, self).save(*args, **kwargs)

    def __str__(self):
        return f"Membership {self.id}"

    class Meta:
        constraints = (
            models.CheckConstraint(name="%(app_label)s_%(class)s_plan_valid", check=models.Q(plan__in=(0, 1))),
        )
