from django.contrib.auth import get_user_model
from django.db import models


class YookassaPayment(models.Model):
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
