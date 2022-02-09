import logging
import uuid
from datetime import timedelta
from django.utils import timezone
from yookassa import Configuration, Payment, Webhook
from yookassa.domain.exceptions import ApiError
from yookassa.domain.response import PaymentResponse

from . import constants
from .models import YookassaPayment
from apps.subscriptions.models import PremiumSubscription
from rentit.settings.components import config
from apps.accounts.models import User

logger = logging.getLogger(__name__)

Configuration.account_id = config("YOOKASSA_ACCOUNT_ID")
Configuration.secret_key = config("YOOKASSA_SECRET_KEY")
Configuration.configure_auth_token(config("YOOKASSA_AUTH_TOKEN"))


def remove_active_webhooks() -> None:
    """Removes all active webhooks on Yookassa"""
    for webhook in Webhook.list().items:
        try:
            Webhook.remove(webhook.id)
        except ApiError as e:
            logger.warning(f"Error removing webhook: {e}")


remove_active_webhooks()

Webhook.add(
    {
        "event": "payment.succeeded",
        "url": f"https://{config('DOMAIN_NAME')}/payments/yookassa_notification/",
    }
)


def process_payment(received_payment: PaymentResponse) -> YookassaPayment:
    """Saves new payment status in database

    Args:
        received_payment: Payment status received from Yookassa

    Returns: Saved payment instance
    """

    stored_payment = YookassaPayment.objects.get(id=received_payment.id)
    stored_payment.status = received_payment.status
    if received_payment.status == constants.YOOKASSA_SUCCEEDED:
        stored_payment.payment_method = received_payment.payment_method.title

    stored_payment.save()
    return stored_payment


def extend_premium_membership(days: int, user: User, payment: YookassaPayment) -> None:
    """Makes Membership premium for a given User and creates a subscription

    Args:
        days: Days since current time for Subscription expiration date.
        user: User model instance
        payment: Payment model instance
    """

    membership = user.membership
    try:
        subscription = PremiumSubscription.objects.get(membership=membership)
        subscription.expiration_date += timedelta(days=days)
        subscription.save()
    except PremiumSubscription.DoesNotExist:
        PremiumSubscription.objects.create(
            membership=user.membership,
            expiration_date=timezone.now() + timedelta(days=days),
            last_payment=payment,
        )
    membership.plan = membership.Plans.PREMIUM
    membership.save()


def allow_new_payment(user: User, minutes_wait: int) -> bool:
    """Indicates if new payment creation is allowed

    Args:
        user: User model object
        minutes_wait: minutes after last payment created

    Returns: True if the last payment status for a given user status is pending
    for more than minutes_wait, or it is not pending. Otherwise, False.

    """
    last_payment = YookassaPayment.objects.filter(user=user).order_by("created_at").last()
    if (
        last_payment
        and last_payment.status == constants.YOOKASSA_PENDING
        and last_payment.created_at > timezone.now() - timedelta(minutes=minutes_wait)
    ):
        return False
    return True


def create_payment(amount: str, return_url: str, description: str, user: User) -> PaymentResponse:
    """Creates a payment in Yookassa and saves it`s info in database

    Args:
        amount: Amount in rubles
        return_url: Redirect URL after payment finished in Yookassa
        description: Payment description
        user: User model object

    """

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
