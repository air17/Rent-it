from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils import timezone
from rentit import settings


class MyUserManager(UserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    picture = models.ImageField(blank=True, upload_to="avatars/")
    phone = models.CharField(max_length=20)

    is_premium = models.BooleanField(default=False, help_text="Доступен ли пользователю премиум-функционал")
    premium_start_date = models.DateTimeField(null=True)
    premium_finish_date = models.DateTimeField(null=True)
    last_payment_id = models.CharField(max_length=100, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = MyUserManager()

    def __str__(self):
        return self.get_full_name()

    def get_avatar_url(self) -> str:
        if self.picture:
            url = self.picture.url
        else:
            url = settings.MEDIA_URL+"user.png"
        return url


class Advertisement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_published = models.DateTimeField(default=timezone.now)
    price = models.PositiveIntegerField()
    address = models.CharField(max_length=150, blank=True, default="Адрес не указан")
    active = models.BooleanField(default=True)

    class FlatCategory(models.TextChoices):
        _ = "", "Тип жилья"  # placeholder
        ROOM = "R", "Комната"
        FLAT = "F", "Квартира"
        HOUSE = "H", "Дом"

    category = models.CharField(max_length=2, choices=FlatCategory.choices, blank=False)

    def __str__(self):
        return self.category + self.name


class AdvertisementImages(models.Model):
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='ad_pics/', )
    main = models.BooleanField(default=False)


class Comment(models.Model):
    # comment author
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comment_author")
    # advertisement author
    profile = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comment_for")
    advertisement = models.ForeignKey(Advertisement, on_delete=models.DO_NOTHING)
    text = models.TextField(blank=False)
    date_published = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.text
