from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from model_utils.models import UUIDModel

from utils.random_filename import RandomFileName


class Advertisement(UUIDModel):
    """Stores an advertisement

    Attributes:
        category: Specifies accommodation type
        name: Advertisement title
        description: Accommodation description
        author: Related User model
        date_published: Date and time the ad published
        price: Accommodation price
        address: Accommodation full address
        active: Defines if advertisement is public
        picture: Accommodation photo

    """

    class FlatCategory(models.TextChoices):
        """Enumerated string choices."""

        _ = "", "Accommodation type"  # placeholder
        ROOM = "ROOM", "Room"
        FLAT = "FLAT", "Flat"
        HOUSE = "HOUSE", "House"

    category = models.CharField(
        max_length=10,
        choices=FlatCategory.choices,
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    author = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    date_published = models.DateTimeField(default=timezone.now)
    price = models.PositiveIntegerField()
    address = models.CharField(
        max_length=150,
        blank=True,
        default="-",
    )
    active = models.BooleanField(default=True)
    picture = models.ImageField(
        verbose_name="Photo",
        upload_to=RandomFileName("advertisements"),
    )

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_category_valid",
                check=models.Q(category__in=("", "ROOM", "FLAT", "HOUSE")),
            ),
        ]


class Comment(models.Model):
    """Stores a comment

    Attributes:
        author: Comment`s author (User model)
        profile: Author of the commented advertisement (User model)
        advertisement: Commented advertisement
        text: Text of the comment
        date_published: Date and time the comment published

    """

    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="comment_author",
        db_index=True,
    )

    profile = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="comment_for",
    )
    advertisement = models.ForeignKey(
        Advertisement,
        on_delete=models.SET_NULL,
        null=True,
        db_index=True,
    )
    text = models.TextField()
    date_published = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.text

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=("author", "advertisement"), name="unique_author_advertisement"),
        )
