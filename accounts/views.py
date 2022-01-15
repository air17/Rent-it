import uuid
from datetime import timedelta
import yookassa
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.generic import DetailView
from yookassa import Payment, Configuration

from rentitapp import models, forms


# profile page
class UserView(DetailView):
    model = get_user_model()
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Adding comments
        comments = models.Comment.objects.filter(profile=self.object)
        context["comments"] = comments

        # Adding active ads
        # Making a list to be able to remove items
        public_ads = list(
            models.Advertisement.objects.filter(author=self.object, active=True))

        # Removing new ads for non-premium users
        if self.request.user.is_anonymous or not self.request.user.is_premium:
            for ad in public_ads:
                if ad.date_published > timezone.now() - timedelta(days=1):
                    public_ads.remove(ad)

        context["public_ads"] = public_ads

        return context


# personal account page
@login_required
def account_view(request):
    template_name = "accounts/account.html"

    user = request.user

    context = {"user": user}

    # Adding comments
    comments = models.Comment.objects.filter(profile=user)
    context["comments"] = comments

    # Adding own ads
    context["active_ads"] = models.Advertisement.objects.filter(
        author=user, active=True)
    context["deactivated_ads"] = models.Advertisement.objects.filter(
        author=user, active=False)

    return render(request, template_name, context)


# user registration
def registration(request):
    if not request.user.is_anonymous:
        return HttpResponseRedirect("/")
    if request.method == 'POST':
        form = forms.RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            new_user = form.save()
            login(request, user=new_user)
            return redirect("rentitapp:account")
    else:
        form = forms.RegistrationForm()
    return render(request, "registration/registration.html", context={"form": form})


@login_required
def premium_view(request):
    context = {"success": False}
    if request.GET.get("success"):
        context = {"success": True}
    payment_processing(request.user)
    return render(request, "accounts/premium_page.html", context)


@login_required
def payment_view(request):
    status = payment_processing(request.user)
    if not status or status == "canceled" or request.GET.get("cancel"):
        payment = Payment.create({
            "amount": {
                "value": "250.00",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "http://127.0.0.1:8000/profile/premium/payment"
            },
            "capture": True,
            "description": "Покупка премиум-доступа на месяц для "+request.user.get_full_name()
        }, uuid.uuid4())

        request.user.last_payment_id = payment.id
        request.user.save()

        return HttpResponseRedirect(payment.confirmation.confirmation_url)
    elif status == "pending":
        return render(request, "accounts/payment_page.html")
    elif status == "succeeded":
        return HttpResponseRedirect("/profile/premium?success=True")
    else:
        # return HttpResponseRedirect("/profile")
        raise ValueError("Wrong payment status")


def payment_processing(user):
    Configuration.account_id = 841788
    Configuration.secret_key = "test_V47LWbfmoVL_XChQn2jNWAG_a3DKPLkiPjRO4KBmOx4"
    if user.last_payment_id:
        payment = yookassa.Payment.find_one(user.last_payment_id)
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
