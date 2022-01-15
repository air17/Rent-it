from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


class Advertisement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
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
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="comment_author")
    # advertisement author
    profile = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="comment_for")
    advertisement = models.ForeignKey(Advertisement, on_delete=models.DO_NOTHING)
    text = models.TextField(blank=False)
    date_published = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.text
