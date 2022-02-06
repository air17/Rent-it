from django.db import models
from django.utils import timezone

from apps.accounts.models import Membership


class PremiumSubscription(models.Model):
    membership = models.OneToOneField(Membership, on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=timezone.now)
    expiration_date = models.DateTimeField()
    last_payment = models.ForeignKey(
        to="payments.YookassaPayment",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"Subscription {self.id} till {self.expiration_date}"
