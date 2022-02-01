from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from utils.random_filename import RandomFileName


class Advertisement(models.Model):
    class FlatCategory(models.TextChoices):
        _ = "", "Тип жилья"  # placeholder
        ROOM = "R", "Комната"
        FLAT = "F", "Квартира"
        HOUSE = "H", "Дом"

    category = models.CharField(max_length=2,
                                choices=FlatCategory.choices,
                                )
    name = models.CharField(max_length=100)
    description = models.TextField()
    author = models.ForeignKey(get_user_model(),
                               on_delete=models.CASCADE,
                               )
    date_published = models.DateTimeField(default=timezone.now)
    price = models.PositiveIntegerField()
    address = models.CharField(max_length=150,
                               blank=True,
                               default="Not specified",
                               )
    active = models.BooleanField(default=True)
    picture = models.ImageField(verbose_name="Photo",
                                upload_to=RandomFileName("advertisements"),
                                )

    def __str__(self):
        return self.name


class Comment(models.Model):
    # comment author
    author = models.ForeignKey(get_user_model(),
                               on_delete=models.CASCADE,
                               related_name="comment_author",
                               )
    # advertisement author
    profile = models.ForeignKey(get_user_model(),
                                on_delete=models.CASCADE,
                                related_name="comment_for",
                                )
    advertisement = models.ForeignKey(Advertisement,
                                      on_delete=models.DO_NOTHING,
                                      )
    text = models.TextField(blank=False,
                            null=False,
                            )
    date_published = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.text
