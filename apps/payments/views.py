import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rentit.settings.components import config
from .services import process_payment, allow_new_payment, create_payment
from ..subscriptions.constants import PREMIUM_SUBSCRIPTION_PRICE


@csrf_exempt
def process_notification(request):
    event_json = json.loads(request.body)
    process_payment(event_json)
    return HttpResponse(status=200)


@login_required
def payment_view(request):
    if allow_new_payment(request.user):
        payment = create_payment(
            amount=PREMIUM_SUBSCRIPTION_PRICE,
            return_url=f"https://{config('DOMAIN_NAME')}/payments/redirect/",
            description="Покупка премиум-доступа на месяц для " + request.user.get_full_name(),
            user=request.user,
        )

        return HttpResponseRedirect(payment.confirmation.confirmation_url)


def payment_processing_view(request):
    return render(request, "payments/payment_processing.html")
