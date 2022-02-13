from django.db import models
from django.utils import timezone

from apps.accounts.models import Membership


class PremiumSubscription(models.Model):
    """Stores a membership subscription info

    Attributes:
        membership: Related Membership
        start_date: Date and time the subscription started
        expiration_date: Date and time the subscription expires
        last_payment: Related YookassaPayment

    """

    membership = models.OneToOneField(Membership, on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=timezone.now)
    expiration_date = models.DateTimeField()
    last_payment = models.ForeignKey(
        # Relation as a string to prevent circular import
        to="payments.YookassaPayment",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"Subscription {self.id} till {self.expiration_date}"
