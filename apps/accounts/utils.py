import uuid
from datetime import timedelta
from django.utils import timezone
from yookassa import Configuration, Payment

from rentit.settings.components import config


def payment_processing(user):
    Configuration.account_id = config("YOOKASSA_ACCOUNT_ID")
    Configuration.secret_key = config("YOOKASSA_SECRET_KEY")
    if not user.last_payment_id:
        return

    payment = Payment.find_one(user.last_payment_id)
    if payment.status == "succeeded":
        user.last_payment_id = None
        user.is_premium = True
        if user.premium_finish_date and user.premium_finish_date > timezone.now():
            user.premium_finish_date += timedelta(days=30)
        else:
            user.premium_finish_date = timezone.now() + timedelta(days=30)
        user.save()
    elif payment.status == "cancelled":
        user.last_payment_id = None
        user.save()

    return payment.status


def create_payment(amount, return_url, description):
    payment = Payment.create(
        {
            "amount": {"value": amount, "currency": "RUB"},
            "confirmation": {"type": "redirect", "return_url": return_url},
            "capture": True,
            "description": description,
        },
        uuid.uuid4(),
    )
    return payment
