import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from yookassa.domain.notification import WebhookNotification

from rentit.settings.components import config

from ..subscriptions.constants import PREMIUM_SUBSCRIPTION_PRICE
from .constants import YOOKASSA_SUCCEEDED
from .services import (
    allow_new_payment,
    create_payment,
    extend_premium_membership,
    process_payment,
)

logger = logging.getLogger(__name__)


@csrf_exempt
def process_notification(request):
    """Processes Yookassa webhook"""
    event = json.loads(request.body)
    try:
        notification_object = WebhookNotification(event)
    except (ValueError, TypeError) as error_message:
        logger.error(str(error_message))
        return HttpResponse(status=400)
    payment = process_payment(notification_object.object)
    if payment.status == YOOKASSA_SUCCEEDED and payment.amount == "250.00":
        extend_premium_membership(30, payment.user, payment)
    return HttpResponse(status=200)


@login_required
def payment_view(request):
    """Creates a new payment on Yookassa and redirects user to it`s page."""
    if allow_new_payment(request.user, 2):
        payment = create_payment(
            amount=PREMIUM_SUBSCRIPTION_PRICE,
            return_url=f"https://{config('DOMAIN_NAME')}/payments/redirect/",
            description="Покупка премиум-доступа на месяц для " + request.user.get_full_name(),
            user=request.user,
        )

        return HttpResponseRedirect(payment.confirmation.confirmation_url)


def payment_processing_view(request):
    """Shows notification that the payment is being processed"""
    return render(request, "payments/payment_processing.html")
