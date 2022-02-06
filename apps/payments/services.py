import logging
import uuid
from datetime import timedelta
from django.utils import timezone
from yookassa import Configuration, Payment, Webhook
from yookassa.domain.exceptions import ApiError
from yookassa.domain.notification import WebhookNotification
from yookassa.domain.response import PaymentResponse

from . import constants
from .models import YookassaPayment
from apps.subscriptions.models import PremiumSubscription
from rentit.settings.components import config

logger = logging.getLogger(__name__)

Configuration.account_id = config("YOOKASSA_ACCOUNT_ID")
Configuration.secret_key = config("YOOKASSA_SECRET_KEY")
Configuration.configure_auth_token(config("YOOKASSA_AUTH_TOKEN"))

for webhook in Webhook.list().items:
    try:
        Webhook.remove(webhook.id)
    except ApiError as e:
        logger.warning(f"Error removing webhook: {e}")

Webhook.add(
    {
        "event": "payment.succeeded",
        "url": f"https://{config('DOMAIN_NAME')}/payments/yookassa_notification/",
    }
)


def process_payment(event_json: dict):
    try:
        notification_object = WebhookNotification(event_json)
    except Exception as err:
        logger.error(str(err))
        return

    payment: PaymentResponse = notification_object.object
    stored_payment = YookassaPayment.objects.get(id=payment.id)

    stored_payment.status = payment.status

    if payment.status == constants.YOOKASSA_SUCCEEDED:
        stored_payment.payment_method = payment.payment_method.title
        stored_payment.processed = True
        extend_premium_membership(30, stored_payment)

    stored_payment.save()


def extend_premium_membership(days: int, stored_payment: YookassaPayment):
    membership = stored_payment.user.membership
    try:
        subscription = PremiumSubscription.objects.get(membership=membership)
        subscription.expiration_date += timedelta(days=days)
        subscription.save()
    except PremiumSubscription.DoesNotExist:
        PremiumSubscription.objects.create(
            membership=stored_payment.user.membership,
            expiration_date=timezone.now() + timedelta(days=days),
            last_payment=stored_payment,
        )
    membership.plan = membership.Plans.PREMIUM
    membership.save()


def allow_new_payment(user):
    last_payment = YookassaPayment.objects.filter(user=user).order_by("created_at").last()

    if (
        last_payment
        and last_payment.status == constants.YOOKASSA_PENDING
        and last_payment.created_at > timezone.now() - timedelta(minutes=2)
    ):
        return False

    return True


def create_payment(amount: str, return_url: str, description: str, user) -> PaymentResponse:
    payment = Payment.create(
        {
            "amount": {"value": amount, "currency": "RUB"},
            "confirmation": {"type": "redirect", "return_url": return_url},
            "capture": True,
            "description": description,
        },
        uuid.uuid4(),
    )

    YookassaPayment.objects.create(
        id=payment.id,
        status=payment.status,
        amount=payment.amount.value,
        user=user,
        created_at=payment.created_at,
        expires_at=payment.expires_at,
    )
    return payment
