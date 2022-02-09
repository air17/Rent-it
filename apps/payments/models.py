from django.contrib.auth import get_user_model
from django.db import models


class YookassaPayment(models.Model):
    """Stores the payment info received from Yookassa

    Attributes:
        id: Payment id on Yookassa
        status: Payment status on Yookassa
        amount: Payment amount in rubles
        user: Related User model
        created_at: Date and time the payment was created
        expires_at: Date and time the payment expires on Yookassa
        payment_method: Payment method received from Yookassa on success
        processed: Specifies if the payment 'succeeded' status received
    """

    id = models.CharField(max_length=100, primary_key=True)
    status = models.CharField(max_length=20)
    amount = models.CharField(max_length=20)
    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    expires_at = models.DateTimeField(null=True)
    payment_method = models.CharField(max_length=255, blank=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.status} payment {self.id}".capitalize()
