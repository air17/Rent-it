from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from . import constants


@login_required
def premium_view(request):
    context = {"price": constants.PREMIUM_SUBSCRIPTION_PRICE}
    return render(request, "subscriptions/status_page.html", context)
